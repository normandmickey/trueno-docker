from flask import request, redirect, url_for
from flask_admin import expose
from wtforms import Form

from app.formatters.common import satoshi_formatter, format_timestamp, \
    format_hash
from app.formatters.lnd import path_formatter
from app.lnd_client.admin.lnd_model_view import LNDModelView
from app.lnd_client.grpc_generated.rpc_pb2 import SendRequest


class PaymentsModelView(LNDModelView):
    can_create = True
    create_form_class = SendRequest
    get_query = 'get_payments'
    primary_key = 'payment_hash'

    list_template = 'admin/lnd/payments_list.html'

    column_list = ['creation_date', 'value', 'fee', 'payment_hash',
                   'payment_preimage', 'path']

    column_formatters = {
        'creation_date': format_timestamp,
        'value': satoshi_formatter,
        'fee': satoshi_formatter,
        'payment_hash': format_hash,
        'payment_preimage': format_hash,
        'path': path_formatter,
    }

    column_default_sort = ('creation_date', True)

    def scaffold_form(self):
        form_class = super(PaymentsModelView, self).scaffold_form()
        return form_class

    def create_model(self, form_data: Form):

        # This depends on whether the form is coming from the Create view or
        # the list view
        if hasattr(form_data, 'data'):
            form_data = form_data.data

        data = {k: v for k, v in form_data.items() if form_data[k]}

        response = self.ln.send_payment_sync(**data)
        if response is False:
            return False

        decoded_pay_req = self.ln.decode_payment_request(
            pay_req=data['payment_request'])
        payments = self.ln.get_payments()
        new_payment = [p for p in payments
                       if p.payment_hash == decoded_pay_req.payment_hash]
        return new_payment[0]

    @expose('/', methods=('GET', 'POST'))
    def index_view(self):

        if request.method == 'POST':
            self.create_model(request.form.copy())
            return redirect(url_for('payment.index_view'))

        FormClass = self.scaffold_form()
        self._template_args['send_payment_form'] = FormClass()

        return super(PaymentsModelView, self).index_view()
