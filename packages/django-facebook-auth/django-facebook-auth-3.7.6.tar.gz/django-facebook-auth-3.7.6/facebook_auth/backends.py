from datetime import datetime
import logging

from facebook_auth import graph_api

try:
    import urllib.parse as urlparse
except ImportError:
    import urlparse

from django.conf import settings
from django.utils import timezone
from facepy import exceptions

from facebook_auth import models
from facebook_auth import utils

logger = logging.getLogger(__name__)


def _truncate(word, length, to_zero=False):
    if to_zero and len(word) > length:
        return word[0:0] # preserve type
    else:
        return word[:length]

FACEBOOK_TIMEOUT = getattr(settings, 'FACEBOOK_AUTH_BACKEND_FACEBOOK_TIMEOUT',
                           timezone.timedelta(seconds=20).total_seconds())


class UserFactory(object):
    fallback_expiration_date = datetime(1990, 10, 10, 0, 0, 1).replace(
        tzinfo=timezone.utc)

    def __create_username(self, profile):
            return profile['id']  # TODO better username

    def _product_user(self, access_token, profile):
        user_id = int(profile['id'])
        username = self.__create_username(profile)
        user, created = models.FacebookUser.objects.get_or_create(
            user_id=user_id, defaults={'username': username})

        if user.username != username:
            logger.warning('FacebookUser username mismatch', extra={
                'old_username': user.username,
                'new_username': username,
                'user_django_id': user.id,
                'user_facebook_id': user_id,
                'user_email': user.email
            })
        if created:
            user.set_unusable_password()

        def copy_field(field, to_zero=False):
            if field in profile:
                length = user._meta.get_field_by_name(field)[0].max_length
                setattr(user, field, _truncate(profile[field], length,
                        to_zero=to_zero))

        copy_field('email', True)
        copy_field('first_name')
        copy_field('last_name')
        if access_token is not None:
            models.FacebookTokenManager().insert_token(
                access_token, str(user.user_id))
        user.save()
        self.create_profile_object(profile, user)
        return user

    def get_user(self, access_token):
        profile = utils.get_from_graph_api(
            graph_api.get_graph(access_token, timeout=FACEBOOK_TIMEOUT),
            'me')
        return self._product_user(access_token, profile)

    def _get_fallback_expiration_date(self):
        logger.warning('Deprecated fallback expiration_date used.')
        return self.fallback_expiration_date

    def get_user_by_id(self, uid):
        api = utils.get_application_graph(
            version=settings.FACEBOOK_API_VERSION
        )
        profile = utils.get_from_graph_api(api, uid)
        return self._product_user(None, profile)

    def create_profile_object(self, profile, user):
        if 'facebook_profile' in settings.INSTALLED_APPS:
            from facebook_profile import models as profile_models
            from facebook_profile import parser as profile_parser
            parser = profile_parser.FacebookDataParser(profile, True, True)
            try:
                data = parser.run()
                profile = (profile_models.FacebookUserProfile
                           .objects.create_or_update(data))
                profile.user = user
                profile.save()
            except profile_parser.FacebookDataParserCriticalError:
                pass


USER_FACTORY = UserFactory()


class FacebookBackend(object):
    def authenticate(self, code=None, redirect_uri=None):
        graph = graph_api.get_graph(timeout=FACEBOOK_TIMEOUT)
        args = {
            'client_id': settings.FACEBOOK_APP_ID,
            'client_secret': settings.FACEBOOK_APP_SECRET,
            'redirect_uri': redirect_uri,
            'code': code
        }
        try:
            data = graph.get('/oauth/access_token', **args)
        except exceptions.FacebookError as e:
            message = "Facebook login failed %s" % e.message
            code_used_message = 'This authorization code has been used.'
            if e.code == 100 and e.message == code_used_message:
                logger.info(message)
                return None
            else:
                logger.warning(message)
                raise
        except exceptions.FacepyError as e:
            logger.warning("Facebook login connection error")
            raise
        try:
            access_token = urlparse.parse_qs(data)['access_token'][-1]
        except KeyError as e:
            args['client_secret'] = '*******%s' % args['client_secret'][-4:]
            logger.error(e, extra={'facebook_response': data,
                                   'sent_args': args})
            return None
        user = USER_FACTORY.get_user(access_token)
        return user

    @staticmethod
    def _timestamp_to_datetime(timestamp):
        naive = datetime.fromtimestamp(int(timestamp))
        return naive.replace(tzinfo=timezone.utc)

    def get_user(self, user_id):
        try:
            return models.FacebookUser.objects.get(pk=user_id)
        except models.FacebookUser.DoesNotExist: #@UndefinedVariable
            return None


class FacebookJavascriptBackend(FacebookBackend):
    def authenticate(self, access_token):
        return USER_FACTORY.get_user(access_token)
