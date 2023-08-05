from django.views.generic import TemplateView

__author__ = 'cenk'


class SimpleStaticView(TemplateView):
    def get_template_names(self):
        return ["index.html"]
