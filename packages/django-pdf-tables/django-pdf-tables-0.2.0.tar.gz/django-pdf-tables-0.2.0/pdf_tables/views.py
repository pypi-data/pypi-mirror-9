from django.views.generic import View

from mixins import PDFMixin, PDFTablesMixin


class PDFView(PDFMixin, View):
    def dispatch(self, request, *args, **kwargs):
        return self.render()


class PDFTableView(PDFTablesMixin, PDFView):
    pass
