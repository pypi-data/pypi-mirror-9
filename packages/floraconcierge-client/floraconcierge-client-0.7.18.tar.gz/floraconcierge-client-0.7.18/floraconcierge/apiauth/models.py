from django.contrib.auth.models import BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from floraconcierge.mapping.model import User as ApiUser


class StaffManager(BaseUserManager):
    def _create_user(self, email, is_staff, is_superuser, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        now = timezone.now()
        if not email:
            raise ValueError('The given email must be set')

        email = self.normalize_email(email)
        user = self.model(email=email,
                          is_staff=is_staff, is_active=True,
                          is_superuser=is_superuser, last_login=now,
                          date_joined=now, **extra_fields)
        user.save(using=self._db)
        return user

    def create_user(self, email, **extra_fields):
        return self._create_user(email, False, False, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        return self._create_user(email, True, True, **extra_fields)


class User(PermissionsMixin):
    email = models.EmailField(unique=True)
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    last_login = models.DateTimeField(_('last login'), default=timezone.now)

    is_staff = models.BooleanField(_('staff status'), default=False,
                                   help_text=_('Designates whether the user can log into this admin '
                                               'site.'))
    is_active = models.BooleanField(_('active'), default=True,
                                    help_text=_('Designates whether this user should be treated as '
                                                'active. Unselect this instead of deleting accounts.'))

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = StaffManager()

    def __init__(self, *args, **kwargs):
        api_user_model = kwargs.pop('api_user_model', None)

        super(User, self).__init__(*args, **kwargs)
        self.info = api_user_model

    @classmethod
    def from_api_user(cls, user):
        assert isinstance(user, ApiUser)

        try:
            obj = cls.objects.get(email=user.email)
            obj.info = user
        except User.DoesNotExist:
            obj = cls(api_user_model=user)

        return obj

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.id or not update_fields:
            return super(User, self).save(force_insert=force_insert, force_update=force_update, using=using,
                                          update_fields=update_fields)

    def get_email(self):
        return self.email or self.info.email

    def get_username(self):
        return self.get_email()

    def is_anonymous(self):
        return self.info is not None

    def is_authenticated(self):
        return bool(self.info)

    def __str__(self):
        return self.get_email()

    def __unicode__(self):
        return self.get_email()

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        swappable = 'AUTH_USER_MODEL'
