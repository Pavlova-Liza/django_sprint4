from django.views.generic import TemplateView


class Rules(TemplateView):
    template_name = "pages/rules.html"


class About(TemplateView):
    template_name = "pages/about.html"


class PageNotFound(TemplateView):
    template_name = 'pages/404.html'
    status = 404


class CsrfFailure(TemplateView):
    template_name = 'pages/403csrf.html'
    status = 403


class ServerError(TemplateView):
    template_name = 'pages/500.html'
    status = 500
