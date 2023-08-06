import json

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


def scope_property():
    def fget(self):
        return self._scope.split()
    def fset(self, value):
        self._scope = ' '.join(value)

    return locals()


class Client(models.Model):

    RESPONSE_TYPE_CHOICES = [
        ('code', 'code (Authorization Code Flow)'),
        ('id_token', 'id_token (Implicit Flow)'),
        ('id_token token', 'id_token token (Implicit Flow)'),
    ]

    name = models.CharField(max_length=100, default='')
    client_id = models.CharField(max_length=255, unique=True)
    client_secret = models.CharField(max_length=255, unique=True)
    response_type = models.CharField(max_length=30,
                                     choices=RESPONSE_TYPE_CHOICES)

    _redirect_uris = models.TextField(default='')

    def redirect_uris():
        def fget(self):
            return self._redirect_uris.splitlines()
        def fset(self, value):
            self._redirect_uris = '\n'.join(value)
        return locals()
    redirect_uris = property(**redirect_uris())

    @property
    def default_redirect_uri(self):
        return self.redirect_uris[0] if self.redirect_uris else ''


class Code(models.Model):

    user = models.ForeignKey(User)
    client = models.ForeignKey(Client)
    code = models.CharField(max_length=255, unique=True)
    expires_at = models.DateTimeField()

    _scope = models.TextField(default='')
    scope = property(**scope_property())

    def has_expired(self):
        return timezone.now() >= self.expires_at


class Token(models.Model):

    user = models.ForeignKey(User)
    client = models.ForeignKey(Client)
    access_token = models.CharField(max_length=255, unique=True)
    expires_at = models.DateTimeField()

    _scope = models.TextField(default='')
    scope = property(**scope_property())

    _id_token = models.TextField()

    def id_token():
        def fget(self):
            return json.loads(self._id_token)
        def fset(self, value):
            self._id_token = json.dumps(value)
        return locals()
    id_token = property(**id_token())


class UserInfo(models.Model):

    user = models.OneToOneField(User, primary_key=True)
    given_name = models.CharField(max_length=255, blank=True, null=True)
    family_name = models.CharField(max_length=255, blank=True, null=True)
    middle_name = models.CharField(max_length=255, blank=True, null=True)
    nickname = models.CharField(max_length=255, blank=True, null=True)
    gender = models.CharField(max_length=100, default='', blank=True, null=True)
    birthdate = models.DateField(null=True)
    zoneinfo = models.CharField(max_length=100, default='', blank=True,
                                null=True)
    locale = models.CharField(max_length=100, default='', blank=True, null=True)
    preferred_username = models.CharField(max_length=255, blank=True, null=True)
    profile = models.URLField(default='', null=True, blank=True)
    picture = models.URLField(default='', null=True, blank=True)
    website = models.URLField(default='', null=True, blank=True)
    email_verified = models.NullBooleanField(default=False)
    locale = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=255, blank=True, null=True)
    phone_number_verified = models.NullBooleanField(default=False)
    address_formatted = models.CharField(max_length=255, blank=True, null=True)
    address_street_address = models.CharField(max_length=255, blank=True,
                                              null=True)
    address_locality = models.CharField(max_length=255, blank=True, null=True)
    address_region = models.CharField(max_length=255, blank=True, null=True)
    address_postal_code = models.CharField(max_length=255, blank=True,
                                           null=True)
    address_country = models.CharField(max_length=255, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    @property
    def name(self):
        name = ''
        if self.given_name:
            name = self.given_name
            if self.family_name:
                name = name + ' ' + self.family_name

        return name
