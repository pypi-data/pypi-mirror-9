from django.db import models
from django.conf import settings
from custom_user.models import AbstractEmailUser
from .managers import CustomUserQuerySet
import re

PATTERN = re.compile(r'^is_(.+)$')


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    
    class Meta:
        abstract = True


class CustomUserMixin(object):
    @property
    def profile(self):
        if not hasattr(self, '_profile'):
            for each in self._meta.get_all_field_names():
                value = getattr(self, each, None)
                if value and isinstance(value, Profile):
                    self._profile = value
        return self._profile
	
    def __getattr__(self, name):
        match = re.match(PATTERN, name)
        if match:
            return self.is_profile(match.group(1))
        raise AttributeError(name)
	
    def is_profile(self, name):
        return bool(getattr(self, name, None))


class AbstractCustomUser(AbstractEmailUser, CustomUserMixin):
    queryset = CustomUserQuerySet.manager()
      
    class Meta:
        abstract = True
          
class CustomUser(AbstractCustomUser):
    pass
    