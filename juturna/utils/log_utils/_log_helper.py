import logging

from juturna.utils.log_utils import _formatters


class _JuturnaLogger:
    def __init__(self):
        self._root_logger = logging.getLogger('jt')
        self._root_handler = logging.StreamHandler()
        self._root_formatter_name = 'full'

        self._root_handler.setFormatter(
            _formatters._FORMATTERS[self._root_formatter_name]
        )
        self._root_handler.addFilter(JuturnaPipelineFilter())
        self._root_logger.addHandler(self._root_handler)
        self._root_logger.propagate = False

    def _logger(self, logger_name: str = '') -> logging.Logger:
        return (
            self._root_logger.getChild(logger_name)
            if logger_name
            else self._root_logger
        )

    def _formatters(self) -> list:
        return list(_formatters._FORMATTERS.keys())

    def _formatter(self, formatter_name: str = '') -> str | None:
        if formatter_name == '':
            return self._root_formatter_name

        self._root_formatter_name = formatter_name
        fmt = _formatters._FORMATTERS[formatter_name]

        for handler in self._root_logger.handlers:
            handler.setFormatter(fmt)


class JuturnaPipelineFilter(logging.Filter):
    _REGISTRY = {}

    @classmethod
    def register_pipeline(cls, pipe_name: str, extras: dict):
        cls._REGISTRY[pipe_name] = extras or dict()

    def filter(self, record):
        parts = record.name.split('.')

        if len(parts) >= 2 and parts[0] == 'jt':
            pipe_name = parts[1]

            extras = self._REGISTRY.get(pipe_name, dict())

            for key, value in extras.items():
                if not hasattr(record, key):
                    setattr(record, key, value)

        return True


_JT_LOGGER = _JuturnaLogger()


def jt_logger(logger_name: str = '') -> logging.Logger:
    return _JT_LOGGER._logger(logger_name)


def formatters() -> list:
    return _JT_LOGGER._formatters()


def formatter(formatter_name: str = '') -> str | None:
    return _JT_LOGGER._formatter(formatter_name)


def add_formatter(name: str, formatter: logging.Formatter):
    _formatters._FORMATTERS[name] = formatter


def add_handler(
    handler: logging.Handler, formatter: str | logging.Formatter = ''
):
    formatter = (
        _formatters._FORMATTERS[formatter or _JT_LOGGER._root_formatter_name]
        if isinstance(formatter, str)
        else formatter
    )

    handler.setFormatter(formatter)
    handler.addFilter(JuturnaPipelineFilter())
    jt_logger().addHandler(handler)


def add_extra(logger_name: str, extra: dict):
    JuturnaPipelineFilter.register_pipeline(logger_name, extra)
