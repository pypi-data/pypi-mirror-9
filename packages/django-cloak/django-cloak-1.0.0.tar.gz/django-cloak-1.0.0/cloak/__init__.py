MAX_AGE_OF_SIGNATURE_IN_SECONDS = 60
SESSION_USER_KEY = "_cloak"
SESSION_REDIRECT_KEY = "_cloak_redirect"

def can_cloak_as(user, other_user):
    """
    Returns true if `user` can cloak as `other_user`
    """
    # check to see if the user is allowed to do this
    can_cloak = False
    try:
        can_cloak = user.can_cloak_as(other_user)
    except AttributeError as e:
        try:
            can_cloak = user.is_staff
        except AttributeError as e:
            pass

    return can_cloak
