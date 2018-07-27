from flask_admin import BaseView, expose

from app.bitcoind_client.bitcoind_client import BitcoinClient


class WalletView(BaseView):
    """
    getwalletinfo
    """

    @expose('/')
    def index(self):
        bitcoin = BitcoinClient()

        wallet_info = bitcoin.get_wallet_info()

        return self.render('admin/bitcoind/wallet.html',
                           wallet_info=wallet_info
                           )

