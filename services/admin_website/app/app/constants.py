import inspect
import os
import string
import random

default_secret_key = ''.join(
    random.choice(string.ascii_uppercase + string.digits) for _ in
    range(20))
FLASK_SECRET_KEY = os.environ.get('FLASK_SECRET_KEY', default_secret_key)

default_network = 'testnet'
NETWORK = os.environ.get('NETWORK', default_network)

constants_file_path = os.path.dirname(inspect.getfile(inspect.currentframe()))
default_lnd_auth_data_path = os.path.abspath(os.path.join(constants_file_path,
                                                          '..', # app
                                                          '..', # admin_website
                                                          '..', # services
                                                          '..', # bitcoin-lightning-docker
                                                          'docker',
                                                          f'lnd-{NETWORK}-data'
                                                          ))
LND_AUTH_DATA_PATH = os.environ.get('LND_AUTH_DATA_PATH',
                                    default_lnd_auth_data_path)

TESTNET_BITCOIN_FAUCET = 'https://testnet.coinfaucet.eu/'

LND_RPC_URI = os.environ.get('LND_RPC_URI', '127.0.0.1:10012')
LND_PEER_URI = os.environ.get('LND_PEER_URI', '127.0.0.1:9736')
