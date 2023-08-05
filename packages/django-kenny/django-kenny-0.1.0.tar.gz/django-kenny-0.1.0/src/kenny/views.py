import os
from django.views.generic import TemplateView
from django.http import Http404
from django.template import TemplateDoesNotExist
from django.template.loader import get_template

# Create your views here.
class SongBirdView(TemplateView):
    prefix = ""
    def get_template_names(self):
        path = "{}.html".format(
            self.kwargs['path'].rstrip('/') or 'index')
        path = os.path.join(self.prefix, path).replace(os.path.sep, "/")
        try:
            get_template(path)
            return [path]
        except TemplateDoesNotExist:
            raise Http404
