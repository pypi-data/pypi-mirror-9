from __future__ import absolute_import
import tempfile
from mock import MagicMock, Mock, patch
from model_mommy.mommy import make, prepare

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.core.urlresolvers import reverse
from django.contrib.auth import REDIRECT_FIELD_NAME

from . import SESSION_USER_KEY, can_cloak_as, SESSION_REDIRECT_KEY
from .middleware import CloakMiddleware
from .views import login, uncloak

class CloakMiddlewareTest(TestCase):
    def test_return_none_if_key_isnt_in_session(self):
        """
        If the special session var isn't set, the middleware should return
        None, and the request.user object should be unchanged
        """
        cm = CloakMiddleware()
        user = Mock()
        request = MagicMock(user=user)
        self.assertEqual(None, cm.process_request(request))
        self.assertEqual(user, request.user)
        self.assertFalse(user.is_cloaked)

    def test_user_does_not_exist_returns_None(self):
        """
        If the user doesn't exist, then return None, and the user object
        shouldn't be changed
        """
        cm = CloakMiddleware()
        user = Mock()
        request = Mock(session={SESSION_USER_KEY: '123'}, user=user)
        self.assertEqual(None, cm.process_request(request))
        self.assertEqual(user, request.user)
        self.assertFalse(user.is_cloaked)

    def test_request_user_is_replaced_when_cloaked(self):
        """
        If the logged in user is allowed to cloak as the other user, the
        request.user object should get replace with the user they are cloaking
        as
        """
        user = make(get_user_model())
        user_to_cloak_as = make(get_user_model())
        cm = CloakMiddleware()
        request = Mock(session={SESSION_USER_KEY: user_to_cloak_as.pk}, user=user)

        with patch("cloak.middleware.can_cloak_as", return_value=True):
            self.assertEqual(None, cm.process_request(request))
            self.assertEqual(request.user, user_to_cloak_as)
            self.assertTrue(request.user.is_cloaked)

    def test_request_user_is_not_replaced_when_not_allowed_to_cloak(self):
        """
        If the logged in user is not allowed to cloak as the other user, the
        request.user object should not be replaced
        """
        user = make(get_user_model())
        user_to_cloak_as = make(get_user_model())
        cm = CloakMiddleware()
        request = Mock(session={SESSION_USER_KEY: user_to_cloak_as.pk}, user=user)

        with patch("cloak.middleware.can_cloak_as", return_value=False):
            self.assertEqual(None, cm.process_request(request))
            self.assertEqual(request.user, user)


class CanCloakAsTest(TestCase):
    def test_is_staff_fallback(self):
        """
        When User.can_cloak_as(other_user) is not defined, we should fallback
        on the is_admin flag
        """
        user = make(get_user_model(), is_staff=True)
        other_user = make(get_user_model())
        self.assertTrue(can_cloak_as(user, other_user))

        user = make(get_user_model(), is_staff=False)
        other_user = make(get_user_model())
        self.assertFalse(can_cloak_as(user, other_user))

    def test_can_cloak_as_method_is_called(self):
        """
        If User.can_cloak_as(other_user) works, that should determine if you
        are allowed to cloak as a user
        """
        user = make(get_user_model())
        user.can_cloak_as = lambda other_user: True
        other_user = make(get_user_model())
        self.assertTrue(can_cloak_as(user, other_user))

        user = make(get_user_model())
        user.can_cloak_as = lambda other_user: False
        other_user = make(get_user_model())
        self.assertFalse(can_cloak_as(user, other_user))


class LoginManagementCommandTest(TestCase):
    def test_favor_superusers_then_staffers(self):
        """
        If there is a superuser or staffer in the system, it should return the
        first one
        """
        user = make(get_user_model(), is_staff=False)
        staffer = make(get_user_model(), is_staff=True)
        other_staffer = make(get_user_model(), is_staff=True)
        superuser = make(get_user_model(), is_superuser=True)

        stdout = tempfile.TemporaryFile(mode="w+")
        call_command("login", stdout=stdout)
        stdout.seek(0)
        content = stdout.read()
        # the first superuser by PK should be the one used
        self.assertIn("/cloak/login/%d" % superuser.pk, content)

        # try again for staffer when there is no superuser
        superuser.delete()
        stdout = tempfile.TemporaryFile(mode="w+")
        call_command("login", stdout=stdout)
        stdout.seek(0)
        content = stdout.read()
        # the first superuser by PK should be the one used
        self.assertIn("/cloak/login/%d" % staffer.pk, content)

    def test_any_user_fallback(self):
        """
        If there are no staffers in the system, then fall back on the first
        user in the system
        """
        user = make(get_user_model(), is_staff=False)
        other_user = make(get_user_model(), is_staff=False)
        stdout = tempfile.TemporaryFile(mode="w+")
        call_command("login", stdout=stdout)
        stdout.seek(0)
        content = stdout.read()
        # the first staffer by PK should be the one used
        self.assertIn("/cloak/login/%d" % user.pk, content)

    def test_timestamp_signer_is_used(self):
        """
        Ensure that the TimestampSigner gets used
        """
        user = make(get_user_model())
        stdout = tempfile.TemporaryFile(mode="w+")
        # we replace the TimestampSigner.sign method to return just the thing that it was passed because this ensures
        with patch("cloak.management.commands.login.TimestampSigner.sign", Mock(return_value=str(user.pk))) as mock:
            call_command("login", stdout=stdout)
            self.assertTrue(mock.called)
        stdout.seek(0)
        content = stdout.read().strip()
        # the first staffer by PK should be the one used
        self.assertEqual("/cloak/login/%d" % user.pk, content)

    def test_no_users_exist(self):
        """
        A command error should be raised if there is a problem
        """
        # the first staffer by PK should be the one used
        self.assertRaises(CommandError, call_command, "login")

    def test_username_field_is_used(self):
        """
        If an argument is specified, the user with the USERNAME_FIELD set to
        that argument should be used
        """
        # cloud the system with a dummy staff user
        make(get_user_model(), is_staff=True)
        # this is the user we actually want to use
        user = make(get_user_model())
        stdout = tempfile.TemporaryFile(mode="w+")
        call_command("login", user.get_username(), stdout=stdout)
        stdout.seek(0)
        content = stdout.read()
        self.assertIn("/cloak/login/%d" % user.pk, content)


class LoginViewTest(TestCase):
    def test_valid_signature_required(self):
        """
        A valid signature should log the user in
        """
        user = make(get_user_model())
        with patch("django.conf.settings.LOGIN_REDIRECT_URL", "/foo"):
            response = self.client.get(reverse(login, args=[TimestampSigner().sign(str(user.pk))]), follow=False)

        self.assertRedirects(response, "/foo", target_status_code=404)
        self.assertEqual(user.pk, self.client.session['_auth_user_id'])
        self.assertEqual('django.contrib.auth.backends.ModelBackend', self.client.session['_auth_user_backend'])

    def test_bad_signature(self):
        """
        A bad or expired signature should return a 403 and the user should not
        be logged in
        """
        with patch("django.core.signing.TimestampSigner.unsign", side_effect=BadSignature):
            response = self.client.get(reverse(login, args=[TimestampSigner().sign("1")]))
        self.assertEqual(response.status_code, 403)

        self.assertNotIn('_auth_user_id', self.client.session.keys())

        with patch("django.core.signing.TimestampSigner.unsign", side_effect=SignatureExpired):
            response = self.client.get(reverse(login, args=[TimestampSigner().sign("1")]))
        self.assertEqual(response.status_code, 403)

        self.assertNotIn('_auth_user_id', self.client.session.keys())


# the AuthenticationMiddleware wraps request.user in a
# SimpleLazyObject, which makes testing harder. So we override it
@patch("django.contrib.auth.middleware.SimpleLazyObject", lambda func: func())
class CloakViewTest(TestCase):
    def test_can_cloak_as_protection(self):
        """
        The can_cloak_as function should dictate if the user can use the view
        """
        user = prepare(get_user_model())
        user.set_password("foobar")
        user.save()
        self.client.login(username=user.username, password="foobar")
        to_cloak_as = make(get_user_model())
        with patch("cloak.views.can_cloak_as", Mock(return_value=False)) as mock:
            response = self.client.post(reverse("cloak", args=[to_cloak_as.pk]))
            mock.assert_called_once_with(user, to_cloak_as)
        self.assertEqual(response.status_code, 403)

    def test_cloak(self):
        """
        Ensure the cloak view will cloak the user if they're allowed to
        """
        user = prepare(get_user_model())
        user.set_password("foobar")
        user.save()
        self.client.login(username=user.username, password="foobar")
        # create a user to cloak as
        to_cloak_as = make(get_user_model())

        with patch("cloak.views.can_cloak_as", return_value=True):
            response = self.client.post(reverse("cloak", args=[to_cloak_as.pk]), data={REDIRECT_FIELD_NAME: "/bar"}, HTTP_REFERER="foo")

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.session[SESSION_USER_KEY], to_cloak_as.pk)
        self.assertEqual(self.client.session[SESSION_REDIRECT_KEY], "foo")
        self.assertRedirects(response, "/bar", target_status_code=404)

        # This is a more complex integration test. From the previous code, user
        # is now cloaked as to_cloak_as. To ensure the middleware does the
        # right thing, we patch the middleware's can_cloak_as so it returns
        # True. Then we make a request to the cloak view (again), and use the
        # call to can_cloak_as as a check to see if request.user got replaced
        # with to_cloak_as.
        with patch("cloak.middleware.can_cloak_as", return_value=True):
            with patch("cloak.views.can_cloak_as", Mock(return_value=False)) as mock:
                response = self.client.post(reverse("cloak", args=[user.pk]))
                # this ensures request.user inside the view got replaced with
                # the user we cloaked as earlier
                mock.assert_called_once_with(to_cloak_as, user)

    def test_uncloak(self):
        # there is a bug in Django that doesn't allow sessions to be saved
        # unless the user is logged in
        # https://code.djangoproject.com/ticket/11475
        user = prepare(get_user_model())
        user.set_password("foobar")
        user.save()
        self.client.login(username=user.username, password="foobar")

        # if the user isn't cloaked, nothing bad should happen
        with self.settings(LOGIN_REDIRECT_URL="/bar"):
            response = self.client.post(reverse("uncloak"))
        self.assertRedirects(response, "/bar", target_status_code=404)

        # add the key to the session to ensure it gets deleted
        session = self.client.session
        session[SESSION_USER_KEY] = 5
        session.save()

        with self.settings(LOGIN_REDIRECT_URL="/bar"):
            response = self.client.post(reverse("uncloak"), data={REDIRECT_FIELD_NAME: "/lame"})
        self.assertNotIn(SESSION_USER_KEY, self.client.session)
        self.assertRedirects(response, "/lame", target_status_code=404)
