from django.contrib.messages import *  # NOQA
from django.template import loader


def RenderedDictMessage(template_name='message.html'):

    class _Decorator(object):
        def __init__(self, func):
            self.func = func

        def __get__(self, obj, type=None):
            return functools.partial(self, obj)

        def __call__(self, *args, **kwargs):
            if isinstance(args[1], dict):
                context = {}
                request = args[0]
                context['request'] = request
                context['message'] = args[1]
                message = loader.render_to_string(template_name, context)
                args = list(args)
                args[1] = message
            self.func(*args, **kwargs)
    return _Decorator


_decorate = RenderedDictMessage(template_name='dictmessages/message.html')


debug = _decorate(debug)
info = _decorate(info)
success = _decorate(success)
warning = _decorate(warning)
error = _decorate(error)
