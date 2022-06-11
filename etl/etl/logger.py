"""Общий класс для логгирования через наследование."""
import logging


class Logger(object):
    """Класс, реализующий логгирование."""

    def __init__(self, name: str, level: int = logging.DEBUG):
        """Инициализация.

        Args:
            name (str): наименование для журналирования
            level (int): уровень журналирования из logging
        """
        logging.basicConfig(
            level=level,
            format='[%(asctime)s][%(levelname)s][%(name)s] %(message)s',
        )
        self.logger = logging.getLogger(name=name)

    def log(self, message: str) -> None:
        """Вывод строки в журнал.

        Args:
            message (str): строка для журналирования
        """
        self.logger.debug(message)
