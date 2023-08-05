from django.views.generic import TemplateView
from crm.contract.models import Contract
from crm.contract.models import Addendum


class AddendumPrintView(TemplateView):
    template_name = "contract/agreement_2013-2014.html"

    def get_context_data(self, user_id, **kwargs):
        return {
            "contract": Addendum.objects.get(id=user_id),
            "user": self.request.user}


class ContractPrintView(TemplateView):
    contract = None

    def get_template_names(self):
        season_name = self.contract.season.name
        return "contract/agreement_{0}.html".format(season_name)

    def get_context_data(self, user_id, **kwargs):
        self.contract = Contract.objects.get(id=user_id)
        return {
            "contract": self.contract,
            "user": self.request.user}


class SamplePrintView(TemplateView):
    template_name = "contract/agreement_2013-2014.html"

    def get_context_data(self, document_id, **kwargs):
        return {
            "contract": Contract.objects.filter(document=document_id)[0],
            "user": self.request.user}
