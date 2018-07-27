from flask_admin import expose
from google.protobuf.json_format import MessageToDict
from markupsafe import Markup

from app.constants import NETWORK, TESTNET_BITCOIN_FAUCET
from app.formatters.common import format_hash, satoshi_formatter
from app.formatters.lnd import tx_hash_formatter
from app.lnd_client.admin.lnd_model_view import LNDModelView
from app.lnd_client.grpc_generated.rpc_pb2 import SendCoinsRequest


class TransactionsModelView(LNDModelView):
    can_create = True
    create_form_class = SendCoinsRequest
    get_query = 'get_transactions'
    primary_key = 'tx_hash'

    list_template = 'admin/lnd/transactions_list.html'

    column_formatters = {
        'tx_hash': tx_hash_formatter,
        'block_hash': format_hash,
        'amount': satoshi_formatter,
        'total_fees': satoshi_formatter,
    }

    def scaffold_form(self):
        form_class = super(TransactionsModelView, self).scaffold_form()
        return form_class

    @expose('/')
    def index_view(self):
        addresses = {
            'p2wkh': self.ln.get_new_address(address_type='WITNESS_PUBKEY_HASH'),
            'np2wkh': self.ln.get_new_address(address_type='NESTED_PUBKEY_HASH')
        }
        if NETWORK == 'testnet':
            addresses['Get testnet coins'] = Markup(
                f'<a target="_blank" href="{TESTNET_BITCOIN_FAUCET}">{TESTNET_BITCOIN_FAUCET}</a>')
        self._template_args['addresses'] = addresses

        balance = self.ln.get_wallet_balance()
        self._template_args['balance'] = MessageToDict(balance)

        return super(TransactionsModelView, self).index_view()
