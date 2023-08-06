
import sys

import gevent
from lithoxyl import Logger
from lithoxyl.sinks import SensibleSink, Formatter, StreamEmitter
from lithoxyl.fields import FormatField


def get_current_gthreadid(record):
    return id(gevent.getcurrent())


class SupportLogger(Logger):
    pass


url_log = SupportLogger('url')
worker_log = SupportLogger('worker')
support_log = SupportLogger('support')


extra_fields = [FormatField('current_gthread_id' , 'd', get_current_gthreadid, quote=False)]


# TODO: create/attach this in context

stderr_fmt = Formatter('{end_local_iso8601_notz} {module_path} ({current_gthread_id}) - {message}',
                       extra_fields=extra_fields)
stderr_emt = StreamEmitter('stderr')
stderr_sink = SensibleSink(formatter=stderr_fmt,
                           emitter=stderr_emt)

url_log.add_sink(stderr_sink)
worker_log.add_sink(stderr_sink)
support_log.add_sink(stderr_sink)

#url_log.critical('serve_http_request').success('{method} {url}', method='GET', url='/')


class LoggingContext(object):
    logger_type = SupportLogger

    def __init__(self, level=None, enable_stderr=True):
        self.level = level
        self.enable_stderr = enable_stderr
        self.loggers = {}
        self.module_loggers = {}
        self.default_logger = support_log

    def get_module_logger(self):
        module_name = sys._getframe(1).f_globals.get('__name__', '<module>')
        try:
            ret = self.module_loggers[module_name]
        except KeyError:
            ret = self.logger_type(name=module_name, module=module_name)
            self.module_loggers[module_name] = ret
            if self.enable_stderr:
                ret.add_sink(stderr_sink)
        return ret

    def get_logger(self, name):
        try:
            ret = self.loggers[name]
        except KeyError:
            ret = self.loggers[name] = self.logger_type(name)
        return ret

    def debug(self, *a, **kw):
        if len(a) == 2:
            log_name, record_name = a
            return self.get_logger(log_name).debug(record_name, **kw)
        return self.default_logger.debug(*a, **kw)

    def info(self, *a, **kw):
        if len(a) == 2:
            log_name, record_name = a
            return self.get_logger(log_name).info(record_name, **kw)
        return self.default_logger.info(*a, **kw)

    def critical(self, *a, **kw):
        if len(a) == 2:
            log_name, record_name = a
            return self.get_logger(log_name).critical(record_name, **kw)
        return self.default_logger.critical(*a, **kw)
