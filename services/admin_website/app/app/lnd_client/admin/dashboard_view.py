from flask_admin import BaseView, expose
from google.protobuf.json_format import MessageToDict

from app.constants import LND_RPC_URI, LND_PEER_URI
from app.lnd_client.lightning_client import LightningClient


class LightningDashboardView(BaseView):
    @expose('/')
    def index(self):
        ln = LightningClient(rpc_uri=LND_RPC_URI, peer_uri=LND_PEER_URI)

        lnd_info = ln.get_info()
        if lnd_info is False:
            lnd_info = {}
        else:
            lnd_info = MessageToDict(lnd_info)


        peers = ln.get_peers()
        if not peers:
            peers = {'No peers': ' '}
        else:
            peers = [MessageToDict(p) for p in peers]

        channels = ln.list_channels()
        if not channels:
            channels = {'No channels': ' '}
        else:
            channels = [MessageToDict(c) for c in channels]

        return self.render('admin/lnd/lnd_dashboard.html',
                           lnd_info=lnd_info,
                           peers=peers,
                           channels=channels)
