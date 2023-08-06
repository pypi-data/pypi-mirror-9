from django.conf import settings
from django.core.exceptions import (
    PermissionDenied,
    ValidationError
)
from django.core.mail import send_mail
from django.core.urlresolvers import reverse_lazy
from django.http import Http404, HttpResponseServerError
from django.shortcuts import render
from django.template import Context, loader
from django.template.loader import render_to_string
from django.views.generic import View
from djohno.utils import is_pretty_from_address
import socket
from smtplib import SMTPException


class BaseFrameView(View):
    def get(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            raise PermissionDenied
        return render(request, 'djohno/frame.html',
                      {'frame_url': self.frame_url,
                       'title': self.title})


class FrameView(BaseFrameView):
    title = 'Djohno: Home'
    frame_url = reverse_lazy('djohno_index')
frame_view = FrameView.as_view()


class Frame403View(BaseFrameView):
    title = 'Djohno: 403 Check'
    frame_url = reverse_lazy('djohno_403')
frame_403_view = Frame403View.as_view()


class Frame404View(BaseFrameView):
    title = 'Djohno: 404 Check'
    frame_url = reverse_lazy('djohno_404')
frame_404_view = Frame404View.as_view()


class Frame500View(BaseFrameView):
    title = 'Djohno: 500 Check'
    frame_url = reverse_lazy('djohno_500')
frame_500_view = Frame500View.as_view()


class FrameEmailView(BaseFrameView):
    title = 'Djohno: Email Check'
    frame_url = reverse_lazy('djohno_email')
frame_email_view = FrameEmailView.as_view()


class IndexView(View):
    def get(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            raise PermissionDenied
        return render(request, 'djohno/index.html')
index_view = IndexView.as_view()


class BaseExceptionView(View):
    exception = None

    def _get_exception(self):
        raise self.exception('Intentionally raised exception to test error '
                             'handling.')

    def get(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            raise PermissionDenied
        self._get_exception()


class Test403View(BaseExceptionView):
    exception = PermissionDenied
test_403 = Test403View.as_view()


class Test404View(BaseExceptionView):
    exception = Http404
test_404 = Test404View.as_view()


class DjohnoTestException(Exception):
    pass


class Test500View(BaseExceptionView):
    exception = DjohnoTestException
test_500 = Test500View.as_view()


class TestEmailView(View):
    def post(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            raise PermissionDenied

        from_address = settings.DEFAULT_FROM_EMAIL

        try:
            is_pretty = is_pretty_from_address(from_address)
        except ValidationError:
            return self.get(request, *args, **kwargs)

        message = render_to_string('djohno/email_body.txt',
                                   {'pretty_from': is_pretty})

        error = None

        try:
            send_mail('djohno email test',
                      message,
                      from_address,
                      [request.user.email, ],
                      fail_silently=False)
        except SMTPException as e:
            error = e
        except socket.error as e:
            error = e

        return render(request, 'djohno/email_sent.html',
                      {'email': request.user.email,
                       'from_email': from_address,
                       'error': error})

    def get(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            raise PermissionDenied

        from_address = settings.DEFAULT_FROM_EMAIL
        try:
            is_pretty = is_pretty_from_address(from_address)
        except ValidationError:
            return render(request, 'djohno/bad_email.html',
                          {'from_email': from_address})

        return render(request, 'djohno/email.html',
                      {'email': request.user.email,
                       'from_email': from_address,
                       'is_pretty': is_pretty})
test_email = TestEmailView.as_view()


def server_error(request, template_name='500.html'):
    tmpl = loader.get_template(template_name)
    context = Context({'STATIC_URL': settings.STATIC_URL})
    return HttpResponseServerError(tmpl.render(context))
