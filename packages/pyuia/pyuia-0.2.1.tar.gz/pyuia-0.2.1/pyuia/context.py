import logging
__all__ = ['AppContext']

_logger = logging.getLogger(__name__)

class AppContext(object):

    def __init__(self, platform):
        self.platform = platform

    def dump_page_source(self, page=None):
        raise NotImplementedError()

    def take_screenshot_as_png(self, page=None):
        raise NotImplementedError()

    def log_screenshot(self, msg, *args, **kwargs):
        if hasattr(self, '_log_screenshot_delegate'):
            self._log_screenshot_delegate(msg, *args, **kwargs)
            return

        msg = msg % args
        level = kwargs['level'] if 'level' in kwargs else logging.INFO
        _logger.log(level, msg)

    def log_page_source(self, msg, *args, **kwargs):
        if hasattr(self, '_log_page_source_delegate'):
            self._log_page_source_delegate(msg, *args, **kwargs)
            return

        msg = msg % args
        level = kwargs['level'] if 'level' in kwargs else logging.INFO
        _logger.log(level, msg)

    def get_initial_logs(self):
        raise NotImplementedError()

    def get_new_logs(self):
        raise NotImplementedError()

    def quit(self):
        raise NotImplementedError()

