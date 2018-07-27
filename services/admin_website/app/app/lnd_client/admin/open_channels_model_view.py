from flask import flash
from flask_admin import expose
from flask_admin.babel import gettext
from flask_admin.model.fields import AjaxSelectField
from google.protobuf.json_format import MessageToDict

from app.formatters.common import satoshi_formatter
from app.formatters.lnd import channel_point_formatter, pub_key_formatter
from app.lnd_client.admin.ajax_model_loaders import PeersAjaxModelLoader
from app.lnd_client.admin.lnd_model_view import LNDModelView
from app.lnd_client.grpc_generated.rpc_pb2 import (
    OpenChannelRequest,
    Peer,
    Channel, ChannelPoint)


class OpenChannelsModelView(LNDModelView):
    peer_ajax_loader = PeersAjaxModelLoader('node_pubkey_string',
                                            options=None,
                                            model=Peer,
                                            placeholder='Select node pubkey')

    can_create = True
    can_delete = True
    create_form_class = OpenChannelRequest
    get_query = 'list_channels'
    primary_key = 'chan_id'

    column_default_sort = 'chan_id'
    form_excluded_columns = ['node_pubkey']
    form_ajax_refs = {
        'node_pubkey_string': peer_ajax_loader
    }
    list_template = 'admin/lnd/channels_list.html'

    column_formatters = {
        'remote_pubkey': pub_key_formatter,
        'channel_point': channel_point_formatter,
        'capacity': satoshi_formatter,
        'local_balance': satoshi_formatter,
        'remote_balance': satoshi_formatter,
        'commit_fee': satoshi_formatter,
        'fee_per_kw': satoshi_formatter,
        'total_satoshis_sent': satoshi_formatter,
        'total_satoshis_received': satoshi_formatter,
        'unsettled_balance': satoshi_formatter,

    }

    def scaffold_form(self):
        form_class = super(OpenChannelsModelView, self).scaffold_form()
        old = form_class.node_pubkey_string
        ajax_field = AjaxSelectField(loader=self.peer_ajax_loader,
                                     label='node_pubkey_string',
                                     allow_blank=True,
                                     description=old.kwargs['description'])
        form_class.node_pubkey_string = ajax_field
        form_class.local_funding_amount.kwargs['default'] = 500000
        form_class.push_sat.kwargs['default'] = 0
        form_class.target_conf.kwargs['default'] = 3
        form_class.sat_per_byte.kwargs['default'] = 250
        form_class.min_htlc_msat.kwargs['default'] = 1
        return form_class

    def delete_model(self, model: Channel):
        txid, index = model.channel_point.split(':')
        channel_point = ChannelPoint(funding_txid_str=txid,
                                     output_index=int(index))
        response = self.ln.close_channel(channel_point=channel_point)
        if response is not False:
            flash(gettext(str(MessageToDict(response))), 'info')
            return True
        else:
            force_response = self.ln.close_channel(channel_point=channel_point,
                                                   force=True)
            if force_response is not False:
                flash(gettext('Force close: ' + str(MessageToDict(force_response))), 'info')
                return True
        return False

    def create_model(self, form):
        data = form.data
        data['node_pubkey_string'] = data['node_pubkey_string'].pub_key
        response = self.ln.open_channel_sync(**data)
        if response is False:
            return False

        # txid = codecs.decode(response.funding_txid_bytes, 'hex')
        # outpoint = ':'.join([txid, str(response.output_index)])
        # new_channel = [c for c in self.ln.get_channels()
        #                if c.channel_point == outpoint][0]
        return Channel()

    @expose('/')
    def index_view(self):
        balance = self.ln.get_channel_balance()
        self._template_args['balance'] = MessageToDict(balance)
        return super(OpenChannelsModelView, self).index_view()
