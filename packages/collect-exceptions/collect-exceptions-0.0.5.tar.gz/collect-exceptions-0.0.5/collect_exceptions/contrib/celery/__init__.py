
import logging
log = logging.getLogger('django')
import traceback as Traceback

from django.conf import settings as django_settings

from celery.signals import task_failure


def register_signal():
    def process_failure_signal(
            sender, task_id, exception,
            traceback, einfo, args, kwargs, **kw):

        func = sender.name
        arg_str = ''
        for arg in args:
            arg_str = arg_str + str(arg) + ', '
        for key, val in kwargs.iteritems():
            arg_str = arg_str + '%s=%s, ' % (key, str(val))
        func = '%s(%s)' % (sender.name, arg_str)

        task_info = [
            'task: %s\n' % func,
            'task id: %s\n' % task_id,
        ]
        task_info = ''.join(task_info)

        type_, value, tb = einfo.exc_info
        exc_info = Traceback.format_exception(type_, value, tb)
        einfo = ''.join(exc_info)
        einfo = task_info + einfo
        log.warning(einfo)
        django_settings.COLLECT_EXCEPTIONS_CONFIG['exception_collector'](einfo)

    log.info('register_signal success')

    task_failure.connect(process_failure_signal, weak=False)
