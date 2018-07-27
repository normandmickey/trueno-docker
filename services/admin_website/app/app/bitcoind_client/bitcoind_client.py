import platform
from typing import Tuple, List
import os

import bitcoin.rpc
from bitcoin.rpc import JSONRPCError

from app.constants import NETWORK


class BitcoinClient(object):
    def __init__(self):
        self.network = NETWORK
        bitcoin.SelectParams(self.network)

    @property
    def proxy(self):

        conf_file = f'bitcoind-{self.network}.conf'

        # Check for the standard spot for configuration files
        if platform.system() == 'Darwin':
            btc_conf_path = os.path.expanduser('~/Library/Application Support/Bitcoin/')
        elif platform.system() == 'Windows':
            btc_conf_path = os.path.join(os.environ['APPDATA'], 'Bitcoin')
        else:
            btc_conf_path = os.path.expanduser('~/.bitcoin')

        if not os.path.exists(os.path.join(btc_conf_path, conf_file)):
            btc_conf_path = os.path.dirname(os.path.abspath(__file__))

        btc_conf_path = os.path.join(btc_conf_path, conf_file)
        return bitcoin.rpc.Proxy(btc_conf_file=btc_conf_path)

    def call(self, command: str, *args):
        try:
            return self.proxy.call(command, *args)
        except JSONRPCError as exc:
            error = exc.error
            return error

    def generate(self, num_blocks_to_mine: int) -> Tuple[str, str]:
        block_hashes = self.call('generate', num_blocks_to_mine)
        num_blocks_mined = len(block_hashes)
        message = f'{num_blocks_mined} blocks mined'
        category = 'info'
        return message, category

    def create_transaction(self):
        destinations = self.get_new_addresses()
        amount = self.get_wallet_info()['balance']


    def get_block_count(self) -> int:
        block_count = self.call('getblockcount')
        return block_count

    def get_block_hash(self, block_height: int) -> str:
        block_hash = self.call('getblockhash', block_height)
        return block_hash

    def get_block(self, block_hash: str = None, verbosity: int = 1) -> dict:

        if block_hash is None:
            block_hash = self.get_best_block_hash()

        block = self.call('getblock', block_hash, verbosity)
        return block

    def get_recent_txid(self):
        block = self.get_block()
        transactions = block['tx']
        return transactions[0]

    def get_blocks(self, last_block_hash: str, count: int = 10) -> List[dict]:
        blocks = []
        find_block_hash = None

        while len(blocks) < count:
            block = self.get_block(find_block_hash or last_block_hash, 1)
            blocks.append(block)
            find_block_hash = block.get('previousblockhash')
            if find_block_hash is None:
                break

        return blocks

    def get_best_block_hash(self) -> str:
        best_block_hash = self.call('getbestblockhash')
        return best_block_hash

    def get_most_recent_blocks(self, count: int = 10) -> List[dict]:
        best_block_hash = self.get_best_block_hash()
        blocks = self.get_blocks(last_block_hash=best_block_hash, count=count)
        return blocks

    def get_network_info(self) -> dict:
        network_info = self.call('getnetworkinfo')
        return network_info

    def get_blockchain_info(self) -> dict:
        blockchain_info = self.call('getblockchaininfo')
        return blockchain_info

    def get_transaction_stats(self) -> dict:
        transaction_stats = self.call('getchaintxstats')
        return transaction_stats

    def get_block_stats(self, block_hash: str = None,
                        block_height: int = None) -> dict:
        too_few_args = block_hash is None and block_height is None
        too_many_args = block_hash is not None and block_height is not None
        if too_few_args or too_many_args:
            raise ValueError('get_block_stats requires either block_hash or block_height')
        block_stats = self.call('getblockstats', block_hash or block_height)
        return block_stats

    def get_mempool_info(self) -> dict:
        mempool_info = self.call('getmempoolinfo')
        return mempool_info

    def get_raw_mempool(self, verbose: bool = True) -> dict:
        mempool_entries = self.call('getrawmempool', verbose)
        return mempool_entries

    def get_mempool_entry(self, txid: str) -> dict:
        mempool_entry = self.call('getmempoolentry', txid)
        return mempool_entry

    def get_raw_transaction(self, txid: str, verbose: bool = True,
                            block_hash: str = None) -> dict:
        tx = self.call('getrawtransaction', txid, verbose, block_hash)
        return tx

    def get_wallet_info(self) -> dict:
        wallet_info = self.call('getwalletinfo')
        return wallet_info

    def get_new_addresses(self, chain: str = None) -> dict:
        address_types = ['bech32', 'p2sh-segwit', 'legacy']
        new_addresses = {t: self.call('getnewaddress', '', t) for t in
                         address_types}
        return new_addresses
