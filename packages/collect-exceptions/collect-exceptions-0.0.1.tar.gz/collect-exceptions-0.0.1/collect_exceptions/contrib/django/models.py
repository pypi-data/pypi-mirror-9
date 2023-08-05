import sys
import logging
log = logging.getLogger('django')
import traceback

from django.conf import settings as django_settings


def my_exception_handler(request, **kwargs):
    try:
        type_, value, tb = sys.exc_info()
        exc_info = traceback.format_exception(type_, value, tb)
        einfo = ''.join(exc_info)
        log.error(einfo)
        django_settings.MYRAVEN_CONFIG['exception_handler'](einfo)
    except Exception, e:
        log.error(e)


def register_handlers():
    from django.core.signals import got_request_exception
    # Connect to Django's internal signal handler
    got_request_exception.connect(my_exception_handler, weak=False)

    log.info('If Celery is installed, register a signal handler')
    if 'djcelery' in django_settings.INSTALLED_APPS:
        try:
            # Celery < 2.5? is not supported
            from collect_exceptions.contrib.celery import register_signal
        except ImportError:
            log.warning('Failed to install Celery error handler')
        else:
            try:
                register_signal()
            except Exception:
                log.warning('Failed to install Celery error handler')


def is_config_ok():
    if not getattr(django_settings, 'MYRAVEN_CONFIG', None):
        log.warning('no MYRAVEN_CONFIG in settings return False')
        return False
    if not django_settings.MYRAVEN_CONFIG.get('captureException', None):
        log.warning('no captureException in MYRAVEN_CONFIG return False')
        return False

    return True


def get_mod_func(callback):
    try:
        dot = callback.rindex('.')
    except ValueError:
        return callback, ''
    return callback[:dot], callback[dot + 1:]


def raven_import_module(name):
    log.debug('raven_import_module name = %s' % name)
    __import__(name)
    return sys.modules[name]


def handle_config():
    if not is_config_ok():
        return False

    captureException = django_settings.MYRAVEN_CONFIG['captureException']
    mod_name, func_name = get_mod_func(captureException)
    log.info('mod_name = %s  func_name = %s' % (mod_name, func_name))
    try:
        mod = raven_import_module(mod_name)
    except Exception, e:
        log.error(e)
        log.error('raven_import_module except return False')
        return False
    else:
        try:
            lookup_func = getattr(mod, func_name)
            if not callable(lookup_func):
                log.error(
                    "Could not import %s.%s. Func is not callable." %
                    (mod_name, func_name))
                return False
            django_settings.MYRAVEN_CONFIG['exception_handler'] = lookup_func
        except AttributeError:
            log.error(
                "Could not import %s.%s. Func is not callable." %
                (mod_name, func_name))
            return False

    log.info('handle_config return True')
    return True


if handle_config():
    register_handlers()
else:
    log.error('collect_exceptions can not register handler')
