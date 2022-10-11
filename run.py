import os
import sys
import toml
import logging
import sentry_sdk
from app.main import app
from loguru import logger
from fastapi import FastAPI
from types import FrameType
from typing import Any, Optional
from multiprocessing import cpu_count
from gunicorn.glogging import Logger
from gunicorn.app.base import BaseApplication
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.httpx import HttpxIntegration
from sentry_sdk.integrations.gnu_backtrace import GnuBacktraceIntegration

config: dict = toml.load("config.toml")

# Enable sentry logging

sentry_sdk.init(os.environ['SENTRY_DSN'], traces_sample_rate=1.0, integrations=[
        RedisIntegration(),
        HttpxIntegration(),
        GnuBacktraceIntegration(),
    ],)

LOG_LEVEL: Any = logging.getLevelName(config['logging']['level'])
JSON_LOGS: bool = config['logging']['json_logs']
WORKERS: int = int(cpu_count() + 1)
BIND: str = f'{os.environ.get("HYPERCORN_HOST")}:{os.environ.get("HYPERCORN_PORT")}'

class InterceptHandler(logging.Handler):
    """Intercept logs and forward them to Loguru.

    Args:
        logging.Handler (Filterer): Handler to filter logs
    """
    def emit(self, record: logging.LogRecord) -> None:
        """Emit a log record."""
        
        # Get corresponding Loguru level if it exists
        level: str | int
        frame: FrameType
        depth: int
        
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


class StubbedGunicornLogger(Logger):
    """Defining a custom logger class to prevent gunicorn from logging to stdout

    Args:
        Logger (object): Gunicon logger class
    """
    def setup(self, cfg) -> None:
        """Setup logger."""
        
        handler: logging.NullHandler = logging.NullHandler()
        self.error_logger: Logger = logging.getLogger("gunicorn.error")
        
        self.error_logger.addHandler(handler)
        
        self.access_logger: Logger = logging.getLogger("gunicorn.access")
        
        self.access_logger.addHandler(handler)
        self.error_logger.setLevel(LOG_LEVEL)
        self.access_logger.setLevel(LOG_LEVEL)


class StandaloneApplication(BaseApplication):
    """Defines a Guicorn application

    Args:
        BaseApplication (object): Base class for Gunicorn applications
    """

    def __init__(self, app: FastAPI, options: dict | None = None):
        """Initialize the application

        Args:
            app (fastapi.FastAPI): FastAPI application
            options (dict, optional): Gunicorn options. Defaults to None.
        """
        self.options: dict = options or {}
        self.application: FastAPI = app
        super().__init__()

    def load_config(self) -> None:
        """Load Gunicorn configuration."""
        config: dict = {
            key: value for key, value in self.options.items()
            if key in self.cfg.settings and value is not None
        }
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self) -> FastAPI:
        """Load the application

        Returns:
            FastAPI: FastAPI application
        """
        return self.application


if __name__ == '__main__':
    intercept_handler = InterceptHandler()
    logging.root.setLevel(LOG_LEVEL)

    seen: set = set()
    for name in [
        *logging.root.manager.loggerDict.keys(),
        "gunicorn",
        "gunicorn.access",
        "gunicorn.error",
        "uvicorn",
        "uvicorn.access",
        "uvicorn.error",
    ]:
        if name not in seen:
            seen.add(name.split(".")[0])
            logging.getLogger(name).handlers = [intercept_handler]

    logger.configure(handlers=[{"sink": sys.stdout, "serialize": JSON_LOGS}])

    options: dict = {
        "bind": BIND,
        "workers": WORKERS,
        "accesslog": "-",
        "errorlog": "-",
        "worker_class": "uvicorn.workers.UvicornWorker",
        "logger_class": StubbedGunicornLogger,
        "preload": True,
    }

    StandaloneApplication(app, options).run()
