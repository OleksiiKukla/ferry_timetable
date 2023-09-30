import logging
import os


def start_logging():
    project_directory = os.path.dirname(os.path.abspath(__file__))
    log_file_path = os.path.join(project_directory, "logs", "telegram_template.log")
    logging.basicConfig(filename=log_file_path, level=logging.DEBUG)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.pool").setLevel(logging.DEBUG)
