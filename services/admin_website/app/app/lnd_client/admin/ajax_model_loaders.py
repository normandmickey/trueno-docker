from typing import List

from flask_admin.model.ajax import AjaxModelLoader, DEFAULT_PAGE_SIZE
from markupsafe import Markup

from app.formatters.lnd import pub_key_formatter
from app.lnd_client.admin.lnd_model_view import LNDModelView
from app.lnd_client.grpc_generated.rpc_pb2 import Channel
from app.lnd_client.peer_directory import peer_directory
from app.lnd_client.peer_directory import Peer

class PeersAjaxModelLoader(AjaxModelLoader):
    def __init__(self, name, model, **options):
        super(PeersAjaxModelLoader, self).__init__(name, options)

        self.model = model

    def format(self, model):
        if model is None:
            return '', ''
        formatted = pub_key_formatter(view=None, context=None, model=model, name='pub_key')
        return model.pub_key, Markup(formatted).striptags()

    def get_one(self, pk):
        return [r for r in LNDModelView(Channel).ln.get_peers()
                if r.pub_key == pk][0]

    def get_list(self, query, offset=0, limit=DEFAULT_PAGE_SIZE):
        pub_keys = LNDModelView(Channel).ln.get_peers()
        return pub_keys


class PeersDirectoryAjaxModelLoader(AjaxModelLoader):
    def __init__(self, name, model, **options):
        super(PeersDirectoryAjaxModelLoader, self).__init__(name, options)

        self.model = model
        self.choices = peer_directory

    def format(self, model: Peer):
        if model is None:
            return '', ''
        formatted = pub_key_formatter(view=None, context=None, model=model, name='pub_key')
        return model.pub_key + '@' + model.address, Markup(formatted).striptags()

    def get_one(self, pk):
        return [r for r in self.choices if r.pub_key == pk][0]

    def get_list(self, query, offset=0, limit=DEFAULT_PAGE_SIZE) -> List[Peer]:
        return list(self.choices.values())
