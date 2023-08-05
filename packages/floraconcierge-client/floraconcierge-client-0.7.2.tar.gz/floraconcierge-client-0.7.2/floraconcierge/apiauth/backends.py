from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from floraconcierge.apiauth.models import User
from floraconcierge.errors import ResultDefaultError
from floraconcierge.shortcuts import get_apiclient
from floraconcierge.shortcuts.users import login, get_logged_user, social_login


class FloraConciergeBackend(ModelBackend):
    def authenticate(self, username=None, password=None, **kwargs):
        email = None
        try:
            validate_email(username)
            email = username
        except ValidationError:
            pass

        if email:
            try:
                return User.from_api_user(login(username, password))
            except ResultDefaultError, e:
                raise ValidationError(e.message)

    def get_user(self, user_id):
        try:
            if not get_apiclient().env.user_auth_key:
                return None

            user = get_logged_user()
            if user:
                return User.from_api_user(user)
        except ResultDefaultError:
            return None


class FloraConciergeOauthBackend(FloraConciergeBackend):
    def authenticate(self, flora_token=None, **kwargs):
        try:
            return User.from_api_user(social_login(flora_token))
        except ResultDefaultError, e:
            raise ValidationError(e.message)
