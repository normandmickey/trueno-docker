from flask import Flask, redirect
from flask_admin import Admin

from app.bitcoind_client.admin.blockchain_view import BlockchainView
from app.bitcoind_client.admin.blocks_model_view import BlocksModelView
from app.bitcoind_client.admin.mempool_entries_model_view import \
    MempoolEntriesModelView
from app.bitcoind_client.admin.transaction_view import TransactionView
from app.bitcoind_client.admin.wallet_view import WalletView
from app.bitcoind_client.models.blocks import Blocks
from app.bitcoind_client.models.mempool_entries import MempoolEntries
from app.constants import FLASK_SECRET_KEY
from app.lnd_client.admin.open_channels_model_view import OpenChannelsModelView
from app.lnd_client.admin.dashboard_view import LightningDashboardView
from app.lnd_client.admin.invoices_model_view import InvoicesModelView
from app.lnd_client.admin.payments_model_view import PaymentsModelView
from app.lnd_client.admin.peers_model_view import PeersModelView
from app.lnd_client.admin.pending_channels import PendingChannelsModelView
from app.lnd_client.admin.transactions_model_view import TransactionsModelView
from app.lnd_client.grpc_generated.rpc_pb2 import (
    Channel,
    Invoice,
    Payment,
    Peer,
    Transaction
)
from app.lnd_client.models.pending_channel import PendingChannel


class App(Flask):
    def __init__(self):
        super().__init__(__name__)
        self.debug = True
        self.config['SECRET_KEY'] = FLASK_SECRET_KEY

        @self.route('/')
        def index():
            return redirect('/admin')

        self.config['FLASK_ADMIN_FLUID_LAYOUT'] = True

        self.admin = Admin(app=self,
                           name='Bitcoin/LN',
                           template_mode='bootstrap3',
                           )
        self.add_bitcoind_views()
        self.add_lnd_views()

    def add_bitcoind_views(self):
        self.admin.add_view(WalletView(name='Wallet Info',
                                       endpoint='bitcoin',
                                       category='Bitcoin'))

        self.admin.add_view(BlockchainView(name='Blockchain',
                                           endpoint='blockchain',
                                           category='Bitcoin'))

        self.admin.add_view(BlocksModelView(Blocks,
                                            name='Blocks',
                                            category='Bitcoin'))

        self.admin.add_view(TransactionView(name='Transaction',
                                            endpoint='bitcoin-transaction',
                                            category='Bitcoin'))

        self.admin.add_view(MempoolEntriesModelView(MempoolEntries,
                                                    name='Mempool Entries',
                                                    category='Bitcoin'))

    def add_lnd_views(self):
        self.admin.add_view(LightningDashboardView(name='Dashboard',
                                                   endpoint='lightning',
                                                   category='LND'))

        self.admin.add_view(TransactionsModelView(Transaction,
                                                  name='LND Transactions',
                                                  category='LND'))

        self.admin.add_view(PeersModelView(Peer,
                                           name='Peers',
                                           category='LND'))

        self.admin.add_view(PendingChannelsModelView(PendingChannel,
                                                  name='Pending Channels',
                                                  category='LND'))

        self.admin.add_view(OpenChannelsModelView(Channel,
                                                  name='Open Channels',
                                                  category='LND'))

        self.admin.add_view(InvoicesModelView(Invoice,
                                              name='Invoices',
                                              category='LND'))

        self.admin.add_view(PaymentsModelView(Payment,
                                              name='Payments',
                                              category='LND'))


if __name__ == '__main__':
    app = App()
    app.run(port=5013)
