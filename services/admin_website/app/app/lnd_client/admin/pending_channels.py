from flask_admin.model import BaseModelView
from google.protobuf.json_format import MessageToDict
from wtforms import Form

from app.constants import LND_PEER_URI, LND_RPC_URI
from app.formatters.common import satoshi_formatter
from app.formatters.lnd import pub_key_formatter, tx_hash_formatter
from app.lnd_client.admin.lnd_model_view import WrappedLightningClient
from app.lnd_client.models.pending_channel import PendingChannel


class PendingChannelsModelView(BaseModelView):
    column_formatters = {
        'remote_node_pub': pub_key_formatter,
        'capacity': satoshi_formatter,
        'closing_txid': tx_hash_formatter,
        'limbo_balance': satoshi_formatter,
        'local_balance': satoshi_formatter,
        'commit_fee': satoshi_formatter,
        'fee_per_kw': satoshi_formatter,
    }
    @property
    def ln(self):
        return WrappedLightningClient(rpc_uri=LND_RPC_URI,
                                      peer_uri=LND_PEER_URI)

    def get_pk_value(self, model):
        pass

    def scaffold_list_columns(self):
        return ['pending_type', 'fee_per_kw', 'limbo_balance', 'commit_weight',
                'remote_node_pub', 'local_balance', 'capacity', 'closing_txid',
                'channel_point', 'commit_fee']

    def scaffold_sortable_columns(self):
        pass

    def scaffold_form(self):
        class NewForm(Form):
            pass

        return NewForm

    def scaffold_list_form(self, widget=None, validators=None):
        pass

    def get_list(self, page, sort_field, sort_desc, search, filters,
                 page_size=None):
        response = self.ln.list_pending_channels()
        pending_channels = []
        pending_types = [
            'pending_open_channels',
            'pending_closing_channels',
            'pending_force_closing_channels',
            'waiting_close_channels'
        ]
        for pending_type in pending_types:
            for pending_channel in getattr(response, pending_type):
                channel_dict = MessageToDict(pending_channel)
                nested_data = channel_dict.pop('channel')
                flat_dict = {**channel_dict, **nested_data}
                flat_dict['pending_type'] = pending_type
                pending_channel_model = PendingChannel(**flat_dict)
                pending_channels.append(pending_channel_model)
        return len(pending_channels), pending_channels

    def get_one(self, id):
        pass

    def create_model(self, form):
        pass

    def update_model(self, form, model):
        pass

    def delete_model(self, model):
        pass
