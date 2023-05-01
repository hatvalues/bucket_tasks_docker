import csv
import os
from datetime import datetime
import logging
from decouple import config

LOG_LOCATION = config('LOG_LOCATION', default='/tmp')

# standardise all logging out puts and conveniently print to screen
class StandardLogger():
    """
    Class to call for standardising logging output.
    Singleton pattern to avoid creating multiple file handles.
    Convenience functions will log to file and print to screen.
    lp_<logging leverl>(msg, to_screen=True)
        log msg with the named logging level. Print to screen or not.
    clear_log()
        Deletes the content of the log file of same name used to instantiate the instance
    """
    __instance = None

    def __init__(self, process_name, to_screen):
        if StandardLogger.__instance is not None:
            raise Exception("""Attempt to create a StandardLogger instance when StandardLogger already exists.
            Use StandardLogger.get_instance() to get or create the singleton.
            """)
        else:
            StandardLogger.__instance = self
        # standardise all logging of processes
        self.log_dir = LOG_LOCATION
        if not os.path.isdir(self.log_dir):
            os.mkdir(self.log_dir)
        self.log_file = f'{self.log_dir}/{process_name}.log'
        self.logger = logging.getLogger(process_name)
        self.logger.setLevel(logging.INFO)
        self.log_handler = logging.FileHandler(self.log_file)
        self.log_handler.setLevel(logging.INFO)
        self.log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.log_handler.setFormatter(self.log_formatter)
        self.logger.addHandler(self.log_handler)
        self.to_screen = to_screen

    def __del__(self):
        self.logger.removeHandler(self.log_handler)
        self.log_handler.close()
        del self.log_handler

    @staticmethod
    def get_instance(process_name, to_screen=True):
        if StandardLogger.__instance is None:
            StandardLogger(process_name, to_screen)
        else:
            StandardLogger.__instance.to_screen = to_screen
        return StandardLogger.__instance
    
    @staticmethod
    def config_print(to_screen):
        StandardLogger.__instance.to_screen = to_screen
        return None

    def clear_log(self):
        if os.path.exists(self.log_file):
            with open(self.log_file, "w") as lf:
                lf.write("")
    # you can log only the usual way, because this class returns a logger
    # the following methods allow logging as usual and simultaneoulsy printing to screen for interactive monitoring
    def log_print(self, level, msg):
        level_switch = {"debug" : self.logger.debug,
                        "info" : self.logger.info,
                        "warning" : self.logger.warning,
                        "error" : self.logger.error
                        }
        level_switch[level](msg)
        if self.to_screen:
            print(f"{level}: {datetime.utcnow().isoformat()} {msg}")
    def lp_debug(self, msg):
        self.log_print("debug", msg)
    def lp_info(self, msg):
        self.log_print("info", msg)
    def lp_warning(self, msg):
        self.log_print("warning", msg)
    def lp_error(self, msg, raise_error=False, type_of_exception=None):
        self.log_print("error", msg)
        if raise_error:
            if type_of_exception:
                raise type_of_exception(msg)
            else:
                raise Exception(msg)

def preproc_csv(file_name : str, header_row=0):
    """Convenience function for csv file.
    
    Parameters
    ----------
    file_name : str
        Path to file
    header_row : int
        Where to find the headers (zero if none). Will skip prior rows.

    Returns
    -------
    List of dict (headers) or list of list (no headers)
    
    """
    if header_row:
        with open(file_name, "r") as f:
            for _ in range(header_row):
                headers = next(f).strip().split(",")
            data = []
            for row in csv.DictReader(f, fieldnames=headers):
                data.append(row)
        return data
    else: # no headers
        pass