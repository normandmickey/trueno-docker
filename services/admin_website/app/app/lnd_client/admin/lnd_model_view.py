import functools
import inspect
import json

from flask import flash
from flask_admin.babel import gettext
from flask_admin.model import BaseModelView
from grpc import StatusCode
from wtforms import Form, StringField, IntegerField, BooleanField, validators

from app.constants import LND_RPC_URI, LND_PEER_URI
from app.lnd_client.lightning_client import LightningClient

wtforms_type_map = {
    3: IntegerField,  # int64
    4: IntegerField,  # uint64
    5: IntegerField,  # int32
    8: BooleanField,  # bool
    9: StringField,  # string
    12: StringField,  # bytes
    13: IntegerField,  # uint32
}


def grpc_error_handling(func):
    @functools.wraps(func)
    def wrapper(*a, **kw):

        try:
            response = func(*a, **kw)
        except Exception as exc:
            if hasattr(exc, '_state'):
                flash(gettext(exc._state.details), 'error')
            else:
                flash(gettext(str(exc)), 'error')
            return False

        if hasattr(response, 'code') and response.code() == StatusCode.UNKNOWN:
            flash(gettext(response._state.details), 'error')
            return False
        elif hasattr(response, 'payment_error') and response.payment_error:
            flash(gettext(str(response.payment_error)), 'error')
            return False
        return response

    return wrapper


def decorate_all_methods(decorator):
    def apply_decorator(cls):
        for k, f in LightningClient.__dict__.items():
            if inspect.isfunction(f):
                setattr(cls, k, decorator(f))
        return cls

    return apply_decorator


@decorate_all_methods(grpc_error_handling)
class WrappedLightningClient(LightningClient):
    pass


class LNDModelView(BaseModelView):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    with open('rpc.swagger.json', 'r') as swagger_file:
        swagger = json.load(swagger_file)

    @property
    def ln(self):
        return WrappedLightningClient(rpc_uri=LND_RPC_URI,
                                      peer_uri=LND_PEER_URI)

    create_form_class = None
    get_query = None
    primary_key = None

    can_view_details = True
    details_modal = True
    create_modal = True
    can_delete = False
    can_edit = False

    list_template = 'admin/lnd/lnd_list.html'

    def get_one(self, record_id):
        record_count, records = self.get_list()
        return [r for r in records
                if str(getattr(r, self.primary_key)) == str(record_id)][0]

    def get_pk_value(self, model):
        return getattr(model, self.primary_key)

    def get_list(self, page=None, sort_field=None, sort_desc=False, search=None,
                 filters=None, page_size=None):


        results = getattr(self.ln, self.get_query)()

        sort_field = sort_field or self.column_default_sort
        if isinstance(sort_field, tuple):
            sort_field, sort_desc = sort_field
        if sort_field is not None:
            results.sort(key=lambda x: getattr(x, sort_field),
                         reverse=sort_desc)

        return len(results), results

    def create_model(self, form):
        return NotImplementedError()

    def update_model(self, form, model):
        return NotImplementedError()

    def delete_model(self, model):
        return NotImplementedError()

    def scaffold_form(self):
        class NewForm(Form):
            pass

        if self.create_form_class is None:
            return NewForm

        for field in self.create_form_class.DESCRIPTOR.fields:

            if self.form_excluded_columns and field.name in self.form_excluded_columns:
                continue

            field_type = field.type

            if field_type == 11:  # Todo: handle "message" type, which is a nested object
                continue

            FormClass = wtforms_type_map[field_type]
            description = self.swagger['definitions'][
                'lnrpc' + self.create_form_class.__name__]['properties'][
                field.name]
            description = description.get('title') or description.get(
                'description')
            if description:
                description = description.replace('/ ', '')
            form_field = FormClass(field.name,
                                   default=field.default_value or None,
                                   description=description,
                                   validators=[validators.optional()]
                                   )
            setattr(NewForm, field.name, form_field)
        return NewForm

    def scaffold_list_form(self, widget=None, validators=None):
        pass

    def scaffold_list_columns(self):
        columns = [field.name for field in self.model.DESCRIPTOR.fields]
        return columns

    def scaffold_sortable_columns(self):
        columns = [field.name for field in self.model.DESCRIPTOR.fields]
        self.column_descriptions = {
            c: self.swagger['definitions'][
                'lnrpc' + self.model.__name__]['properties'][c].get('title', '').replace('/ ', '')
            for c in columns
        }
        return columns
