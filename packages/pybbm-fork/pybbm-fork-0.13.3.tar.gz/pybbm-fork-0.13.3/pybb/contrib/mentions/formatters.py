from . import settings
from .signals import mentioned

from pybb.compat import get_user_model


def mention(tag_name, value, options, parent, context):
    User = get_user_model()

    if 'mention' not in options:
        return settings.PYBB_MENTIONS_MENTION_FORMAT_WITHOUT_USER % {
            'username': value
        }

    user_id = options['mention']

    try:
        user = User.objects.get(pk=user_id)
    except (User.DoesNotExist, ValueError):
        return settings.PYBB_MENTIONS_MENTION_FORMAT_WITHOUT_USER % {
            'username': value
        }
    else:
        if 'obj' in context and context['obj'] and context['obj'].user:
            mentioned.send(sender=User, user=user, post=context['obj'])

        return settings.PYBB_MENTIONS_MENTION_FORMAT_WITH_USER % {
            'user_url': settings.PYBB_MENTIONS_USER_URL(user),
            'username': value
        }
