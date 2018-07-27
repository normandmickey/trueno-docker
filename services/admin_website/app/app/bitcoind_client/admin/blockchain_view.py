import os

from flask_admin import expose, BaseView

from app.bitcoind_client.bitcoind_client import BitcoinClient
from app.constants import NETWORK


class BlockchainView(BaseView):
    """
    getnetworkinfo
    getblockchaininfo
    getchaintxstats
    getblockstats
    """

    @expose('/')
    def index(self):
        bitcoin = BitcoinClient()

        network_info = bitcoin.get_network_info()
        blockchain_info = bitcoin.get_blockchain_info()
        transaction_stats = bitcoin.get_transaction_stats()
        block_stats = bitcoin.get_block_stats(block_hash=blockchain_info['bestblockhash'])

        websocket_port = os.environ.get('WEBSOCKET_PORT', 8765)

        return self.render('admin/bitcoind/blockchain.html',
                           websocket_port=websocket_port,
                           network_info=network_info,
                           blockchain_info=blockchain_info,
                           transaction_stats=transaction_stats,
                           block_stats=block_stats,
                           network=NETWORK,
                           )

