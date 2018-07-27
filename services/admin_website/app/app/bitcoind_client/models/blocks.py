from app.utilities import DefaultModel


class Blocks(DefaultModel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not hasattr(self, 'previousblockhash'):
            self.previousblockhash = ''
