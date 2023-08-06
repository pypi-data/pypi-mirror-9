# -*- coding: utf-8 -*-

from social_publisher import core, misc

_core = core.PublisherCore()


class Catcher(object):
    SocialUserDoesNotExist = core.SocialUserDoesNotExist

    def __init__(self, user):
        self.user = user

    def __getattr__(self, name):
        def _publish(*args, **kw):
            obj = kw.get('obj', args[0])

            try:
                comment = kw.get('comment', args[1])
            except IndexError:
                comment = None

            _core.publish(self.user, name, obj, comment, **kw)

        return misc._safe_call(_publish)


class PublisherForUserMixin(object):
    @property
    def publish(self):
        return Catcher(user=self)

    @property
    def publisher(self):
        return _core

    def publish_to(self, provider, obj, comment=None, **kw):
        return _core.publish(self, provider, obj, comment, **kw)
