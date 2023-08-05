
import logging
log = logging.getLogger('django')

from django.conf import settings as django_settings

from celery.signals import task_failure


def register_signal():
    def process_failure_signal(
            sender, task_id, exception,
            traceback, einfo, args, kwargs, **kw):

        einfo = str(einfo)
        log.warning(einfo)
        django_settings.COLLECT_EXCEPTIONS_CONFIG['exception_collector'](einfo)

    log.info('register_signal success')

    task_failure.connect(process_failure_signal, weak=False)
