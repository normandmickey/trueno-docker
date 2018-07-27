from flask import request, redirect, url_for
from flask_admin import expose
from flask_admin.model.fields import AjaxSelectField
from wtforms import Form, StringField

from app.formatters.lnd import pub_key_formatter
from app.lnd_client.admin.ajax_model_loaders import \
    PeersDirectoryAjaxModelLoader
from app.lnd_client.admin.lnd_model_view import LNDModelView
from app.lnd_client.grpc_generated.rpc_pb2 import LightningAddress, Peer as LND_Peer
from app.lnd_client.peer_directory import Peer


class PeersModelView(LNDModelView):
    can_create = True
    can_delete = True
    create_form_class = LightningAddress
    get_query = 'get_peers'
    primary_key = 'pub_key'

    column_default_sort = 'pub_key'
    list_template = 'admin/lnd/peers_list.html'
    column_formatters = {
        'pub_key': pub_key_formatter
    }

    peer_directory_ajax_loader = PeersDirectoryAjaxModelLoader(
        'pubkey_at_host',
        options=None,
        model=Peer,
        placeholder='pubkey@host')

    form_ajax_refs = {
        'pubkey_at_host': peer_directory_ajax_loader
    }

    def scaffold_form(self, quick_select=False) -> Form:
        form_class = super(PeersModelView, self).scaffold_form()

        if quick_select:
            ajax_field = AjaxSelectField(loader=self.peer_directory_ajax_loader,
                                         label='pubkey_at_host',
                                         allow_blank=True,
                                         description='pubkey@host')

            form_class.pubkey_at_host = ajax_field
        else:
            form_class.pubkey_at_host = StringField(
                label='pubkey_at_host',
                description='pubkey@host')
        return form_class

    def create_model(self, form_data):

        # This depends on whether the form is coming from the Create view or
        # the list view
        if hasattr(form_data, 'data'):
            form_data = form_data.data

        if form_data.get('pubkey_at_host'):
            pubkey = form_data.get('pubkey_at_host').split('@')[0]
            host = form_data.get('pubkey_at_host').split('@')[1]
        else:
            pubkey = form_data.get('pubkey')
            host = form_data.get('host')

        response = self.ln.connect_peer(pubkey=pubkey, host=host)
        if response is False:
            return False

        new_peer = [p for p in self.ln.get_peers() if p.pub_key == pubkey][0]
        return new_peer

    def delete_model(self, model: LND_Peer):
        response = self.ln.disconnect_peer(pub_key=model.pub_key)
        if response is not False:
            return True
        return False

    @expose('/', methods=('GET', 'POST'))
    def index_view(self):

        if request.method == 'POST':
            self.create_model(request.form.copy())
            return redirect(url_for('peer.index_view'))

        FormClass = self.scaffold_form(quick_select=True)
        self._template_args['add_peer_form'] = FormClass()

        return super(PeersModelView, self).index_view()
