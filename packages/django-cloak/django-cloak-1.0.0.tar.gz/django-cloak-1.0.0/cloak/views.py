from django.conf import settings
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.contrib.auth import get_user_model, login as django_login, REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from django.utils.http import is_safe_url
from . import MAX_AGE_OF_SIGNATURE_IN_SECONDS, SESSION_USER_KEY, SESSION_REDIRECT_KEY, can_cloak_as

# no permissions necessary since this only works for valid signatures
def login(request, signature):
    """
    Automatically logs in a user based on a signed PK of a user object. The
    signature should be generated with the `login` management command.

    The signature will only work for 60 seconds.
    """
    signer = TimestampSigner()
    try:
        pk = signer.unsign(signature, max_age=MAX_AGE_OF_SIGNATURE_IN_SECONDS)
    except (BadSignature, SignatureExpired) as e:
        return HttpResponseForbidden("Can't log you in")

    user = get_object_or_404(get_user_model(), pk=pk)
    # we *have* to set the backend for this user, so we just use the first one
    user.backend = settings.AUTHENTICATION_BACKENDS[0]
    django_login(request, user)

    return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)

@login_required
@require_POST
def cloak(request, pk=None):
    """
    Masquerade as a particular user and redirect based on the
    REDIRECT_FIELD_NAME parameter, or the LOGIN_REDIRECT_URL.

    Callers can either pass the pk of the user in the URL itself, or as a POST
    param.
    """
    pk = request.POST.get('pk', pk)
    if pk is None:
        return HttpResponse("You need to pass a pk POST parameter, or include it in the URL")

    user = get_object_or_404(get_user_model(), pk=pk)

    if not can_cloak_as(request.user, user):
        return HttpResponseForbidden("You are not allowed to cloak as this user")

    request.session[SESSION_USER_KEY] = user.pk
    # save the referer information so when uncloaking, we can redirect the user
    # back to where they were
    request.session[SESSION_REDIRECT_KEY] = request.META.get("HTTP_REFERER", settings.LOGIN_REDIRECT_URL)

    # redirect the cloaked user to the URL specified in the "next" parameter,
    # or to the default redirect URL
    return HttpResponseRedirect(request.POST.get(REDIRECT_FIELD_NAME, settings.LOGIN_REDIRECT_URL))

# no perms neccessary here
@require_POST
def uncloak(request):
    """
    Undo a masquerade session and redirect the user back to where they started
    cloaking from (or where ever the "next" POST parameter points)
    """
    try:
        del request.session[SESSION_USER_KEY]
    except KeyError:
        pass # who cares

    # figure out where to redirect
    next = request.POST.get(REDIRECT_FIELD_NAME) or request.session.get(SESSION_REDIRECT_KEY)
    if next and is_safe_url(next, request.get_host()):
        return HttpResponseRedirect(next)
    return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
