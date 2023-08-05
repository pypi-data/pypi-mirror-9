from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from crm.contract.models import Document


class DocumentAdmin(admin.ModelAdmin):
    change_list_template = "admin/change_list_filter_sidebar.html"
    list_select_related = True
    list_filter = ["season", "type"]
    search_fields = ["name", "type"]
    list_display = ["season", "name", "type", "view_sample_url"]
    list_display_links = ["name"]

    def view_sample_url(self, document):
        return "<a href='/contract/print/sample/%s/'>%s</a>" % (document.id, _("View sample"))
    view_sample_url.allow_tags = True
    view_sample_url.short_description = _("View sample")

    class Media():
        js = [
            "grappelli/tinymce/jscripts/tiny_mce/tiny_mce.js",
            "contract/js/tinymce-setup.js"]
        css = {"all": ["contract/css/contract.css"]}


admin.site.register(Document, DocumentAdmin)
