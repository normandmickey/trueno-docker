from app.utilities import DefaultModel


class PendingChannel(DefaultModel):
    def __getattribute__(self, name):
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            return None