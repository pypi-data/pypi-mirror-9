from django.contrib.auth import get_user_model
from . import SESSION_USER_KEY, can_cloak_as

class CloakMiddleware(object):
    """
    This middleware class checks to see if a cloak session variable is
    set, and overrides the request.user object with the cloaked user
    """
    def process_request(self, request):
        request.user.is_cloaked = False
        if SESSION_USER_KEY in request.session:
            User = get_user_model()
            try:
                user = User._default_manager.get(pk=request.session[SESSION_USER_KEY])
            except User.DoesNotExist:
                return None

            if can_cloak_as(request.user, user):
                request.user = user
                request.user.is_cloaked = True
