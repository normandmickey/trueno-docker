from wtforms import Form

from app.lnd_client.admin.lnd_model_view import LNDModelView
from app.lnd_client.grpc_generated.rpc_pb2 import Invoice


class InvoicesModelView(LNDModelView):
    can_create = True
    create_form_class = Invoice
    get_query = 'get_invoices'
    primary_key = 'payment_request'

    def scaffold_form(self):
        form_class = super(InvoicesModelView, self).scaffold_form()
        return form_class


    def create_model(self, form: Form):
        form_data = form.data
        for key, value in form_data.items():
            if not value:
                form_data[key] = None
        self.ln.create_invoice(**form_data)
