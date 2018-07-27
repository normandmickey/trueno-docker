from datetime import datetime

from flask_admin import expose, BaseView

from app.bitcoind_client.bitcoind_client import BitcoinClient


class TransactionView(BaseView):
    """
    getrawtransaction
    """

    @expose('/')
    @expose('/<txid>/')
    def index(self, txid=None):
        bitcoin = BitcoinClient()

        if txid is None:
            txid = bitcoin.get_recent_txid()

        transaction = bitcoin.get_raw_transaction(txid)
        blocktime_date = datetime.fromtimestamp(transaction['blocktime'])
        transaction['blocktime'] = str(blocktime_date) + ' (' + str(transaction['blocktime']) + ')'

        tooltips = {
            'txid': 'An identifier used to uniquely identify a particular transaction; specifically, the sha256d hash of the transaction.',
            'hash': 'The transaction hash (differs from txid for witness transactions)',
            'size': 'The serialized transaction size',
            'vsize': 'The virtual transaction size (differs from size for witness transactions)',
            'weight': "The transaction's weight (between vsize*4-3 and vsize*4)",
            'version': 'Each transaction is prefixed by a four-byte transaction version number which tells Bitcoin peers and miners which set of rules to use to validate it.',
            'locktime': 'Indicates the earliest time or earliest block when that transaction may be added to the block chain.',
            'blockhash': 'Hash of the block the transaction was included in.',
            'confirmations': 'A score indicating the number of blocks on the best block chain that would need to be modified to remove or modify a particular transaction.',
            'blocktime': 'The block time is a Unix epoch time when the miner started hashing the header (according to the miner). Must be strictly greater than the median time of the previous 11 blocks. Full nodes will not accept blocks with headers more than two hours in the future according to their clock.',
        }

        metadata = [
            'txid',
            'hash',
            'size',
            'vsize',
            'weight',
            'version',
            'locktime',
            'blockhash',
            'confirmations',
            'blocktime',
        ]


        return self.render('admin/bitcoind/transaction.html',
                           transaction=transaction,
                           tooltips=tooltips,
                           metadata=metadata
                           )
