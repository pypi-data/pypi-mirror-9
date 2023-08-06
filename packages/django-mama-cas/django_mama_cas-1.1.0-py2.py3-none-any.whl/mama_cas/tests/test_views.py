from __future__ import unicode_literals

from mock import patch

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import RequestFactory
from django.test.utils import override_settings

from .factories import UserFactory
from .factories import ProxyGrantingTicketFactory
from .factories import ProxyTicketFactory
from .factories import ServiceTicketFactory
from .factories import ConsumedServiceTicketFactory
from .utils import build_url
from mama_cas.forms import LoginForm
from mama_cas.models import ProxyTicket
from mama_cas.models import ServiceTicket
from mama_cas.request import SamlValidateRequest
from mama_cas.views import ProxyView
from mama_cas.views import ProxyValidateView
from mama_cas.views import ServiceValidateView
from mama_cas.views import ValidateView
from mama_cas.views import SamlValidateView


class LoginViewTests(TestCase):
    user_info = {'username': 'ellen',
                 'password': 'mamas&papas'}
    warn_info = {'username': 'ellen',
                 'password': 'mamas&papas',
                 'warn': 'on'}
    service_url = 'http://www.example.com/'

    def setUp(self):
        self.user = UserFactory()

    def test_login_view(self):
        """
        When called with no parameters, a ``GET`` request to the view
        should display the correct template with a login form.
        """
        response = self.client.get(reverse('cas_login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'mama_cas/login.html')
        self.assertTrue(isinstance(response.context['form'], LoginForm))

    def test_login_view_cache(self):
        """
        A response from the view should contain the correct cache-
        control header.
        """
        response = self.client.get(reverse('cas_login'))
        self.assertTrue('Cache-Control' in response)
        self.assertEqual(response['Cache-Control'], 'max-age=0')

    def test_login_view_login(self):
        """
        When called with a valid username and password and no service,
        a ``POST`` request to the view should authenticate and login
        the user, and redirect to the correct view.
        """
        response = self.client.post(reverse('cas_login'), self.user_info)
        self.assertEqual(int(self.client.session['_auth_user_id']), self.user.pk)
        self.assertRedirects(response, reverse('cas_login'))

    def test_login_view_login_service(self):
        """
        When called with a logged in user, a ``GET`` request to the
        view with the ``service`` parameter set should create a
        ``ServiceTicket`` and redirect to the supplied service URL
        with the ticket included.
        """
        response = self.client.post(reverse('cas_login'), self.user_info)
        response = self.client.get(reverse('cas_login'), {'service': self.service_url})
        self.assertEqual(ServiceTicket.objects.count(), 1)
        st = ServiceTicket.objects.latest('id')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'].startswith(self.service_url))
        self.assertTrue(st.ticket in response['Location'])

    @override_settings(MAMA_CAS_VALID_SERVICES=('http://[^\.]+\.example\.org',))
    def test_login_view_invalid_service(self):
        """
        When called with an invalid service URL, the view should
        return a 403 Forbidden response.
        """
        response = self.client.get(reverse('cas_login'), {'service': self.service_url, 'gateway': 'true'})
        self.assertEqual(response.status_code, 403)

    def test_login_view_login_post(self):
        """
        When called with a valid username, password and service, a
        ``POST`` request to the view should authenticate and login the
        user, create a ``ServiceTicket`` and redirect to the supplied
        service URL with the ticket included.
        """
        url = reverse('cas_login') + "?service=%s" % self.service_url
        response = self.client.post(url, self.user_info)
        self.assertEqual(int(self.client.session['_auth_user_id']), self.user.pk)
        self.assertEqual(ServiceTicket.objects.count(), 1)
        st = ServiceTicket.objects.latest('id')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'].startswith(self.service_url))
        self.assertTrue(st.ticket in response['Location'])

    def test_login_view_renew(self):
        """
        When called with a logged in user, a ``GET`` request to the
        view with the ``renew`` parameter should display the login page.
        """
        response = self.client.post(reverse('cas_login'), self.user_info)
        response = self.client.get(reverse('cas_login'), {'service': self.service_url, 'renew': 'true'})
        self.assertTemplateUsed(response, 'mama_cas/login.html')

    def test_login_view_gateway(self):
        """
        When called without a logged in user, a ``GET`` request to the
        view with the ``gateway`` and ``service`` parameters set
        should simply redirect the user to the supplied service URL.
        """
        response = self.client.get(reverse('cas_login'), {'service': self.service_url, 'gateway': 'true'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], self.service_url)

    def test_login_view_gateway_auth(self):
        """
        When called with a logged in user, a ``GET`` request to the
        view with the ``gateway`` and ``service`` parameters set
        should create a ``ServiceTicket`` and redirect to the supplied
        service URL with the ticket included.
        """
        response = self.client.post(reverse('cas_login'), self.user_info)
        response = self.client.get(reverse('cas_login'), {'service': self.service_url, 'gateway': 'true'})
        self.assertEqual(ServiceTicket.objects.count(), 1)
        st = ServiceTicket.objects.latest('id')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'].startswith(self.service_url))
        self.assertTrue(st.ticket in response['Location'])

    @override_settings(MAMA_CAS_ALLOW_AUTH_WARN=True)
    def test_login_view_warn_session(self):
        """
        When a user logs in with the warn parameter present, the user's
        session should contain a ``warn`` attribute.
        """
        self.client.post(reverse('cas_login'), self.warn_info)
        self.assertEqual(self.client.session.get('warn'), True)

    @override_settings(MAMA_CAS_ALLOW_AUTH_WARN=True)
    def test_login_view_warn_auth_redirect(self):
        """
        When a logged in user requests a ``ServiceTicket`` and the
        ``warn`` attribute is set, it should redirect to the warn view
        with the appropriate parameters.
        """
        self.client.post(reverse('cas_login'), self.warn_info)
        response = self.client.get(reverse('cas_login'), {'service': self.service_url})
        self.assertTrue(reverse('cas_warn') in response['Location'])
        self.assertTrue("service=" in response['Location'])
        self.assertTrue('ticket=ST-' in response['Location'])

    @override_settings(MAMA_CAS_ALLOW_AUTH_WARN=True)
    def test_login_view_warn_auth_gateway_redirect(self):
        """
        When a logged in user requests a ``ServiceTicket`` with the
        gateway parameter and the ``warn`` attribute is set, it should
        redirect to the warn view with the appropriate parameters.
        """
        self.client.post(reverse('cas_login'), self.warn_info)
        response = self.client.get(reverse('cas_login'), {'service': self.service_url, 'gateway': 'true'})
        self.assertTrue(reverse('cas_warn') in response['Location'])
        self.assertTrue("service=" in response['Location'])
        self.assertTrue('ticket=ST-' in response['Location'])


@override_settings(MAMA_CAS_ALLOW_AUTH_WARN=True)
class WarnViewTests(TestCase):
    user_info = {'username': 'ellen',
                 'password': 'mamas&papas'}
    url = 'http://www.example.com'

    def setUp(self):
        self.user = UserFactory()

    def test_warn_view_display(self):
        """
        When called with a logged in user, a request to the warn view
        should display the correct template containing the provided
        service string.
        """
        self.client.login(username=self.user_info['username'],
                          password=self.user_info['password'])
        st = ServiceTicketFactory()
        response = self.client.get(reverse('cas_warn'), {'service': self.url, 'ticket': st.ticket})
        self.assertContains(response, self.url, count=3)
        self.assertContains(response, st.ticket)
        self.assertTemplateUsed(response, 'mama_cas/warn.html')

    def test_warn_view_anonymous_user(self):
        """
        When a user is not logged in, a request to the view should
        redirect to the login view.
        """
        response = self.client.get(reverse('cas_warn'))
        self.assertRedirects(response, reverse('cas_login'))

    @override_settings(MAMA_CAS_VALID_SERVICES=('[^\.]+\.example\.org',))
    def test_warn_view_invalid_service(self):
        """
        Whan in invalid service is provided, a request to the view
        should redirect to the login view.
        """
        self.client.login(username=self.user_info['username'],
                          password=self.user_info['password'])
        response = self.client.get(reverse('cas_warn'), {'service': self.url})
        self.assertRedirects(response, reverse('cas_login'))


@override_settings(MAMA_CAS_VALID_SERVICES=('[^\.]+\.example\.com',))
@override_settings(MAMA_CAS_FOLLOW_LOGOUT_URL=False)
class LogoutViewTests(TestCase):
    user_info = {'username': 'ellen',
                 'password': 'mamas&papas',
                 'email': 'ellen@example.com'}
    url = 'http://www.example.com'

    def setUp(self):
        self.user = UserFactory()

    def test_logout_view(self):
        """
        When called with no parameters and no logged in user, a ``GET``
        request to the view should simply redirect to the login view.
        """
        response = self.client.get(reverse('cas_logout'))
        self.assertRedirects(response, reverse('cas_login'))
        self.assertTrue('Cache-Control' in response)
        self.assertEqual(response['Cache-Control'], 'max-age=0')

    def test_logout_view_success(self):
        """
        When called with a logged in user, a ``GET`` request to the
        view should log the user out and display the correct template.
        """
        response = self.client.post(reverse('cas_login'), self.user_info)
        response = self.client.get(reverse('cas_logout'))
        self.assertRedirects(response, reverse('cas_login'))
        self.assertFalse('_auth_user_id' in self.client.session)

    @override_settings(MAMA_CAS_FOLLOW_LOGOUT_URL=True)
    def test_logout_view_follow_service(self):
        """
        When called with a logged in user and MAMA_CAS_FOLLOW_LOGOUT_URL
        is set to ``True``, a ``GET`` request containing ``service``
        should log the user out and redirect to the supplied URL.
        """
        response = self.client.post(reverse('cas_login'), self.user_info)
        response = self.client.get(reverse('cas_logout'), {'service': self.url})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], self.url)
        self.assertFalse('_auth_user_id' in self.client.session)

    @override_settings(MAMA_CAS_FOLLOW_LOGOUT_URL=True)
    def test_logout_view_follow_url(self):
        """
        When called with a logged in user and MAMA_CAS_FOLLOW_LOGOUT_URL
        is set to ``True``, a ``GET`` request containing ``url`` should
        log the user out and redirect to the supplied URL.
        """
        response = self.client.post(reverse('cas_login'), self.user_info)
        response = self.client.get(reverse('cas_logout'), {'url': self.url})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], self.url)
        self.assertFalse('_auth_user_id' in self.client.session)

    def test_logout_view_display_url(self):
        """
        A request containing ``url`` should log the user out and
        display the supplied URL.
        """
        response = self.client.post(reverse('cas_login'), self.user_info)
        response = self.client.get(reverse('cas_logout'), {'url': self.url}, follow=True)
        self.assertRedirects(response, reverse('cas_login'))
        messages = list(response.context['messages'])
        self.assertEqual(messages[1].tags, 'success')
        self.assertTrue(self.url in messages[1].message)

    @override_settings(MAMA_CAS_ENABLE_SINGLE_SIGN_OUT=True)
    def test_logout_single_sign_out(self):
        """
        When called with a logged in user and MAMA_CAS_ENABLE_SINGLE_SIGN_OUT
        is set to ``True``, a ``GET`` request to the view should issue
        a POST request for each service accessed by the user.
        """
        ConsumedServiceTicketFactory()
        ConsumedServiceTicketFactory()
        self.client.post(reverse('cas_login'), self.user_info)
        with patch('requests.post') as mock:
            self.client.get(reverse('cas_logout'))
            self.assertEqual(mock.call_count, 2)


class ValidateViewTests(TestCase):
    url = 'http://www.example.com/'
    url2 = 'http://www.example.org/'

    def setUp(self):
        self.st = ServiceTicketFactory()
        self.rf = RequestFactory()

    def test_validate_view(self):
        """
        When called with no parameters, a validation failure should
        be returned.
        """
        request = self.rf.get(reverse('cas_validate'))
        response = ValidateView.as_view()(request)
        self.assertContains(response, "no\n\n")
        self.assertEqual(response.get('Content-Type'), 'text/plain')

    @override_settings(MAMA_CAS_VALID_SERVICES=('[^\.]+\.example\.com',))
    def test_validate_view_invalid_service(self):
        """
        When called with an invalid service identifier, a validation
        failure should be returned.
        """
        request = self.rf.get(reverse('cas_validate'), {'service': self.url2, 'ticket': self.st.ticket})
        response = ValidateView.as_view()(request)
        self.assertContains(response, "no\n\n")
        self.assertEqual(response.get('Content-Type'), 'text/plain')

    def test_validate_view_invalid_ticket(self):
        """
        When the provided ticket cannot be found, a validation failure
        should be returned.
        """
        st_str = ServiceTicket.objects.create_ticket_str()
        request = self.rf.get(reverse('cas_validate'), {'service': self.url, 'ticket': st_str})
        response = ValidateView.as_view()(request)
        self.assertContains(response, "no\n\n")
        self.assertEqual(response.get('Content-Type'), 'text/plain')

    def test_validate_view_success(self):
        """
        When called with valid parameters, a validation success should
        be returned. The provided ticket should then be consumed.
        """
        request = self.rf.get(reverse('cas_validate'), {'service': self.url, 'ticket': self.st.ticket})
        response = ValidateView.as_view()(request)
        self.assertContains(response, "yes\nellen\n")
        self.assertEqual(response.get('Content-Type'), 'text/plain')

        st = ServiceTicket.objects.get(ticket=self.st.ticket)
        self.assertTrue(st.is_consumed())


class ServiceValidateViewTests(TestCase):
    url = 'http://www.example.com/'
    url2 = 'https://www.example.org/'

    def setUp(self):
        self.st = ServiceTicketFactory()
        self.rf = RequestFactory()

    def test_service_validate_view(self):
        """
        When called with no parameters, a validation failure should
        be returned.
        """
        request = self.rf.get(reverse('cas_service_validate'))
        response = ServiceValidateView.as_view()(request)
        self.assertContains(response, 'INVALID_REQUEST')

    def test_service_validate_view_invalid_service(self):
        """
        When called with an invalid service identifier, a validation
        failure should be returned.
        """
        request = self.rf.get(reverse('cas_service_validate'), {'service': self.url2, 'ticket': self.st.ticket})
        response = ServiceValidateView.as_view()(request)
        self.assertContains(response, 'INVALID_SERVICE')

    def test_service_validate_view_invalid_ticket(self):
        """
        When the provided ticket cannot be found, a validation failure
        should be returned.
        """
        st_str = ServiceTicket.objects.create_ticket_str()
        request = self.rf.get(reverse('cas_service_validate'), {'service': self.url, 'ticket': st_str})
        response = ServiceValidateView.as_view()(request)
        self.assertContains(response, 'INVALID_TICKET')

    def test_service_validate_view_proxy_ticket(self):
        """
        When a proxy ticket is provided, the validation failure should
        indicate that it was because a proxy ticket was provided.
        """
        pt_str = ProxyTicket.objects.create_ticket_str()
        request = self.rf.get(reverse('cas_service_validate'), {'service': self.url, 'ticket': pt_str})
        response = ServiceValidateView.as_view()(request)
        self.assertContains(response, 'INVALID_TICKET')
        self.assertContains(response, 'Proxy tickets cannot be validated'
                                      ' with /serviceValidate')

    def test_service_validate_view_success(self):
        """
        When called with valid parameters, a validation success should
        be returned. The provided ticket should then be consumed.
        """
        request = self.rf.get(reverse('cas_service_validate'), {'service': self.url, 'ticket': self.st.ticket})
        response = ServiceValidateView.as_view()(request)
        self.assertContains(response, 'authenticationSuccess')
        self.assertEqual(response.get('Content-Type'), 'text/xml')

        st = ServiceTicket.objects.get(ticket=self.st.ticket)
        self.assertTrue(st.is_consumed())

    def test_service_validate_view_pgturl(self):
        """
        When called with valid parameters and a ``pgtUrl``, the
        validation success should include a ``ProxyGrantingTicket``.
        """
        request = self.rf.get(reverse('cas_service_validate'), {'service': self.url, 'ticket': self.st.ticket, 'pgtUrl': self.url2})
        with patch('requests.get') as mock:
            mock.return_value.status_code = 200
            response = ServiceValidateView.as_view()(request)
        self.assertContains(response, 'authenticationSuccess')
        self.assertContains(response, 'proxyGrantingTicket')

    def test_service_validate_view_pgturl_http(self):
        """
        When called with valid parameters and an invalid ``pgtUrl``,
        the validation success should have no ``ProxyGrantingTicket``.
        """
        request = self.rf.get(reverse('cas_service_validate'), {'service': self.url, 'ticket': self.st.ticket, 'pgtUrl': self.url})
        response = ServiceValidateView.as_view()(request)
        self.assertContains(response, 'authenticationSuccess')
        self.assertNotContains(response, 'proxyGrantingTicket')

    @override_settings(MAMA_CAS_VALID_SERVICES=('[^\.]+\.example\.net',))
    def test_service_validate_view_invalid_service_url(self):
        """
        When ``MAMA_CAS_VALID_SERVICES`` is defined, a validation
        failure should be returned if the service URL does not match.
        """
        request = self.rf.get(reverse('cas_service_validate'), {'service': self.url, 'ticket': self.st.ticket})
        response = ServiceValidateView.as_view()(request)
        self.assertContains(response, 'INVALID_SERVICE')

    @override_settings(MAMA_CAS_ATTRIBUTE_CALLBACKS=('mama_cas.callbacks.user_name_attributes',))
    def test_service_validate_view_attribute_callbacks(self):
        """
        When a custom callback is defined, a validation success should
        include the returned attributes.
        """
        request = self.rf.get(reverse('cas_service_validate'), {'service': self.url, 'ticket': self.st.ticket})
        response = ServiceValidateView.as_view()(request)
        self.assertContains(response, 'attributes')
        self.assertContains(response, '<cas:username>ellen</cas:username>')


class ProxyValidateViewTests(TestCase):
    url = 'http://www.example.com/'
    url2 = 'https://www.example.com/'

    def setUp(self):
        self.st = ServiceTicketFactory()
        self.pgt = ProxyGrantingTicketFactory()
        self.pt = ProxyTicketFactory()
        self.rf = RequestFactory()

    def test_proxy_validate_view(self):
        """
        When called with no parameters, a validation failure should
        be returned.
        """
        request = self.rf.get(reverse('cas_proxy_validate'))
        response = ProxyValidateView.as_view()(request)
        self.assertContains(response, 'INVALID_REQUEST')

    def test_proxy_validate_view_invalid_service(self):
        """
        When called with an invalid service identifier, a validation
        failure should be returned.
        """
        request = self.rf.get(reverse('cas_proxy_validate'), {'service': self.url2, 'ticket': self.pt.ticket})
        response = ProxyValidateView.as_view()(request)
        self.assertContains(response, 'INVALID_SERVICE')

    def test_proxy_validate_view_invalid_ticket(self):
        """
        When the provided ticket cannot be found, a validation
        failure should be returned.
        """
        pt_str = ProxyTicket.objects.create_ticket_str()
        request = self.rf.get(reverse('cas_proxy_validate'), {'service': self.url, 'ticket': pt_str})
        response = ProxyValidateView.as_view()(request)
        self.assertContains(response, 'INVALID_TICKET')

    def test_proxy_validate_view_st_success(self):
        """
        When called with a valid ``ServiceTicket``, a validation
        success should be returned. The provided ticket should be
        consumed.
        """
        request = self.rf.get(reverse('cas_proxy_validate'), {'service': self.url, 'ticket': self.st.ticket})
        response = ProxyValidateView.as_view()(request)
        self.assertContains(response, 'authenticationSuccess')
        self.assertEqual(response.get('Content-Type'), 'text/xml')

        st = ServiceTicket.objects.get(ticket=self.st.ticket)
        self.assertTrue(st.is_consumed())

    def test_proxy_validate_view_pt_success(self):
        """
        When called with a valid ``ProxyTicket``, a validation success
        should be returned. The provided ticket should be consumed.
        """
        request = self.rf.get(reverse('cas_proxy_validate'), {'service': self.url, 'ticket': self.pt.ticket})
        response = ProxyValidateView.as_view()(request)
        self.assertContains(response, 'authenticationSuccess')
        self.assertEqual(response.get('Content-Type'), 'text/xml')

        pt = ProxyTicket.objects.get(ticket=self.pt.ticket)
        self.assertTrue(pt.is_consumed())

    def test_proxy_validate_view_proxies(self):
        """
        A validation success should include a ``proxies`` block
        containing all the proxies involved.
        """
        pgt2 = ProxyGrantingTicketFactory(granted_by_pt=self.pt,
                                          granted_by_st=None)
        pt2 = ProxyTicketFactory(service='http://ww2.example.com',
                                 granted_by_pgt=pgt2)
        request = self.rf.get(reverse('cas_proxy_validate'), {'service': pt2.service, 'ticket': pt2.ticket})
        response = ProxyValidateView.as_view()(request)
        self.assertContains(response, 'authenticationSuccess')
        self.assertContains(response, 'http://ww2.example.com')
        self.assertContains(response, 'http://www.example.com')

    def test_proxy_validate_view_pgturl(self):
        """
        When called with valid parameters and a ``pgtUrl``, a
        validation success should include a ``ProxyGrantingTicket``.
        """
        request = self.rf.get(reverse('cas_proxy_validate'), {'service': self.url, 'ticket': self.pt.ticket, 'pgtUrl': self.url2})
        with patch('requests.get') as mock:
            mock.return_value.status_code = 200
            response = ProxyValidateView.as_view()(request)
        self.assertContains(response, 'authenticationSuccess')
        self.assertContains(response, 'proxyGrantingTicket')

    def test_proxy_validate_view_pgturl_http(self):
        """
        When called with valid parameters and an invalid ``pgtUrl``,
        the validation success should have no ``ProxyGrantingTicket``.
        """
        request = self.rf.get(reverse('cas_proxy_validate'), {'service': self.url, 'ticket': self.pt.ticket, 'pgtUrl': self.url})
        response = ProxyValidateView.as_view()(request)
        self.assertContains(response, 'authenticationSuccess')
        self.assertNotContains(response, 'proxyGrantingTicket')

    @override_settings(MAMA_CAS_VALID_SERVICES=('^[^\.]+\.example\.net',))
    def test_proxy_validate_view_invalid_service_url(self):
        """
        When ``MAMA_CAS_VALID_SERVICES`` is defined, a validation
        failure should be returned if the service URL does not match.
        """
        request = self.rf.get(reverse('cas_proxy_validate'), {'service': self.url, 'ticket': self.pt.ticket})
        response = ProxyValidateView.as_view()(request)
        self.assertContains(response, 'INVALID_SERVICE')


class ProxyViewTests(TestCase):
    url = 'http://www.example.com/'
    url2 = 'http://www.example.org/'

    def setUp(self):
        self.st = ServiceTicketFactory()
        self.pgt = ProxyGrantingTicketFactory()
        self.rf = RequestFactory()

    def test_proxy_view(self):
        """
        When called with no parameters, a validation failure should be
        returned.
        """
        request = self.rf.get(reverse('cas_proxy'))
        response = ProxyView.as_view()(request)
        self.assertContains(response, 'INVALID_REQUEST')

    def test_proxy_view_no_service(self):
        """
        When called with no service identifier, a validation failure
        should be returned.
        """
        request = self.rf.get(reverse('cas_proxy'), {'pgt': self.pgt.ticket})
        response = ProxyView.as_view()(request)
        self.assertContains(response, 'INVALID_REQUEST')

    def test_proxy_view_invalid_ticket(self):
        """
        When the provided ticket cannot be found, a validation failure
        should be returned.
        """
        pgt_str = ProxyTicket.objects.create_ticket_str()
        request = self.rf.get(reverse('cas_proxy'), {'targetService': self.url, 'pgt': pgt_str})
        response = ProxyView.as_view()(request)
        self.assertContains(response, 'BAD_PGT')

    def test_proxy_view_success(self):
        """
        When called with valid parameters, a validation success
        should be returned.
        """
        request = self.rf.get(reverse('cas_proxy'), {'targetService': self.url, 'pgt': self.pgt.ticket})
        response = ProxyView.as_view()(request)
        self.assertContains(response, 'proxyTicket')

    @override_settings(MAMA_CAS_VALID_SERVICES=('[^\.]+\.example\.com',))
    def test_proxy_view_invalid_service_url(self):
        """
        When called with an invalid service identifier, a proxy
        authentication failure should be returned.
        """
        request = self.rf.get(reverse('cas_proxy'), {'targetService': self.url2, 'pgt': self.pgt.ticket})
        response = ProxyView.as_view()(request)
        self.assertContains(response, 'INVALID_SERVICE')


class SamlValidationViewTests(TestCase):
    url = 'http://www.example.com/'
    url2 = 'https://www.example.org/'

    def setUp(self):
        self.st = ServiceTicketFactory()
        self.rf = RequestFactory()

    def test_saml_validation_view(self):
        """
        When called with no parameters, a validation failure should be
        returned.
        """
        request = self.rf.post(reverse('cas_saml_validate'))
        response = SamlValidateView.as_view()(request)
        self.assertContains(response, 'samlp:RequestDenied')

    def test_saml_validation_view_invalid_service(self):
        """
        When called with an invalid service identifier, a validation
        failure should be returned.
        """
        saml = SamlValidateRequest(context={'ticket': self.st})
        request = self.rf.post(build_url('cas_saml_validate', target=self.url2),
                               saml.render_content(), content_type='text/xml')
        response = SamlValidateView.as_view()(request)
        self.assertContains(response, 'samlp:RequestDenied')

    def test_saml_validation_view_invalid_ticket(self):
        """
        When the provided ticket cannot be found, a validation failure
        should be returned.
        """
        temp_st = ServiceTicketFactory()
        saml = SamlValidateRequest(context={'ticket': temp_st})
        temp_st.delete()
        request = self.rf.post(build_url('cas_saml_validate', target=self.url),
                               saml.render_content(), content_type='text/xml')
        response = SamlValidateView.as_view()(request)
        self.assertContains(response, 'samlp:RequestDenied')

    def test_saml_validation_view_success(self):
        """
        When called with valid parameters, a validation success should
        be returned. The provided ticket should then be consumed.
        """
        saml = SamlValidateRequest(context={'ticket': self.st})
        request = self.rf.post(build_url('cas_saml_validate', target=self.url),
                               saml.render_content(), content_type='text/xml')
        response = SamlValidateView.as_view()(request)
        self.assertContains(response, 'samlp:Success')

        st = ServiceTicket.objects.get(ticket=self.st.ticket)
        self.assertTrue(st.is_consumed())
