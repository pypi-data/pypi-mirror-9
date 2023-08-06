# django-cloak

[![Build Status](https://travis-ci.org/PSU-OIT-ARC/django-cloak.svg?branch=master)](https://travis-ci.org/PSU-OIT-ARC/django-cloak)

cloak is an app that allows administrative users to browse the site as a different user. It also includes a management command (`login`) to generate a login link for a particular user.

## Installation

1. pip install django-cloak
1. Add `cloak` to your INSTALLED_APPS setting
1. Add `cloak.middleware.CloakMiddleware` to your `MIDDLEWARE_CLASSES` (after session and auth middleware)
1. Add `url(r'^cloak/', include('cloak.urls'))` to your urls.py

## Requirements

SessionMiddleware and django.contrib.auth

## Usages

### Command line

    ./manage.py login user_identifier

where `user_identifier` is the value of the USERNAME_FIELD field of your user model.

This will spit out a path you can append to your site's base URL, which will automatically log you in as that user.

**Note**: The backend associated with the user (i.e. the value of `user.backend`) will be the first backend listed in AUTHENTICATION_BACKENDS.

Without a user_identifier, the command will try to find a user with `is_superuser=True`, or `is_staff=True`, or any user, in that order.

### Templates

To cloak as a user, create a form that POSTs to the cloaking URL. The URL can either contain the PK of the user, or you can pass the PK as a POST parameter:

    <form method="post" action="{% url 'cloak' user.pk %}">
        {% csrf_token %}
        <input type="submit" name="submit" value="Cloak" />
    </form>

or

    <form method="post" action="{% url 'cloak' %}">
        {% csrf_token %}
        <select name="pk">
            <option value="1">Matt</option>
            <option value="2">Thom</option>
            <option value="3">Brandon</option>
        </select>
        <input type="submit" name="submit" value="Cloak" />
    </form>

## Other Information

You can tell if a user is cloaked by checking the "is_cloaked" attribute on the user object (this flag is set in the middleware).

When determining if a user is allowed to cloak, the cloak view tries to call a `request.user.can_cloak_as(other_user)` method. If no such method is defined, the code falls back on the `request.user.is_staff` flag.
