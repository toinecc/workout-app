import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import typer
from rich.console import Console
from rich.containers import Renderables
from rich.logging import RichHandler
from rich.table import Table
from rich.text import Text

DEFAULT_FORMAT = "%(message)s"
ENV_LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "INFO")
ENV_LOGGING_FORMAT = os.getenv("LOGGING_FORMAT", DEFAULT_FORMAT)


class CustomRichHandler(RichHandler):
    """Custom RichHandler that reorders columns to: TIME | LEVEL | PATH:LINE | MESSAGE"""

    def render(
        self,
        *,
        record: logging.LogRecord,
        traceback: Optional[Any],
        message_renderable: Any,
    ) -> Table:
        """Render log with custom column order."""

        # Create table with custom column order
        output = Table.grid(padding=(0, 1))
        output.expand = False  # Expand to use full console width

        # Add columns in desired order: TIME | LEVEL | PATH:LINE | MESSAGE
        output.add_column(style="log.time")
        output.add_column(style="log.level", width=8)
        output.add_column(style="log.path", overflow="ellipsis", width=20)
        output.add_column(ratio=1, style="log.message", overflow="fold")

        # Prepare row data
        row = []

        # 1. Time
        log_time = datetime.fromtimestamp(record.created)
        time_format = None if self.formatter is None else self.formatter.datefmt
        time_format = time_format or "[%x %X]"
        log_time_display = Text(log_time.strftime(time_format))
        row.append(log_time_display)

        # 2. Level
        level = self.get_level_text(record)
        row.append(level)

        # 3. Path:line
        path = Path(record.pathname).name
        path_text = Text()
        path_text.append(
            path,
            style=f"link file://{record.pathname}" if self.enable_link_path else "",
        )
        path_text.append(":")
        path_text.append(
            f"{record.lineno}",
            style=f"link file://{record.pathname}#{record.lineno}"
            if self.enable_link_path
            else "",
        )
        row.append(path_text)

        # 4. Message (and traceback if present)
        row.append(
            Renderables(  # type: ignore
                [message_renderable]
                if not traceback
                else [message_renderable, traceback]
            )
        )

        # Add row to table
        output.add_row(*row)

        return output


def get_console_handler(format: str) -> CustomRichHandler:
    """Get a console handler using CustomRichHandler.

    Parameters
    ----------
    format : str
        logs format

    Returns
    -------
    logging.Handler
        CustomRichHandler
    """
    formatter = logging.Formatter(format, datefmt="%Y-%m-%d %H:%M:%S")
    console = Console(width=850)  # , force_terminal=True, force_interactive=False)
    console_handler = CustomRichHandler(
        rich_tracebacks=True,
        tracebacks_suppress=[typer],
        console=console,
        show_time=True,
        show_level=True,
        show_path=True,
    )
    console_handler.setFormatter(formatter)

    return console_handler


def get_logger(
    logger_name: str,
    level: str = ENV_LOGGING_LEVEL,
    format: str = ENV_LOGGING_FORMAT,
) -> logging.Logger:
    """Get a logger.

    Parameters
    ----------
    logger_name : str
        Logger's name. Usually the module's name.
    level : str
        Logging level, by default ENV_LOGGING_LEVEL
    format : str
        logs format, by default ENV_LOGGING_FORMAT

    Returns
    -------
    logging.Logger
        logger
    """
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)
    logger.addHandler(get_console_handler(format=format))
    logger.propagate = True

    return logger

