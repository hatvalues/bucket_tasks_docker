import os
from google.cloud import storage
from datetime import datetime
import logging

GCS_PROJECT_ID = os.getenv("DATASTORE_PROJECT_ID", "hatvalues-sandbox")
BUCKET_NAME = os.getenv("BUCKET_NAME", "data-ingest-bk")
LOGGING_BUCKET_NAME = os.getenv("LOGGING_BUCKET_NAME", "logging-bktasks")
GCS_PROJECT_ID = os.getenv("DATASTORE_PROJECT_ID")

storage_client = storage.Client()

# standardise all logging out puts and conveniently print to screen
class StandardLogger():
    """
    Class to call for standardising logging output.
    Convenience functions will log to file and print to screen.

    lp_<logging leverl>(msg, to_screen=True)
        log msg with the named logging level. Print to screen or not.

    clear_log()
        Deletes the content of the log file of same name used to instantiate the instance
    """
    def __init__(self, process_name):
        # standardise all logging of processes
        self.log_dir = os.getenv("LOG_LOCATION") or "logs"
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
    # BUG: When this class is called in another module
    # it must be actively deleted to kill the file reference.
    # Also, actively check that the logger is not in globals
    # If not, lines will be duplicated on the log file as a second (third, fourth) reference is opened
    def __del__(self):
        self.logger.removeHandler(self.log_handler)
        self.log_handler.close()
        del self.log_handler
    def clear_log(self):
        if os.path.exists(self.log_file):
            with open(self.log_file, "w") as lf:
                lf.write("")
    # you can log only the usual way, because this class returns a logger
    # the following methods allow logging as usual and simultaneoulsy printing to screen for interactive monitoring
    def log_print(self, level, msg, to_screen):
        level_switch = {"debug" : self.logger.debug,
                        "info" : self.logger.info,
                        "warning" : self.logger.warning,
                        "error" : self.logger.error
                        }
        level_switch[level](msg)
        if to_screen:
            print(f"{level}: {datetime.utcnow().isoformat()} {msg}")
    def lp_debug(self, msg, to_screen=True):
        self.log_print("debug", msg, to_screen)
    def lp_info(self, msg, to_screen=True):
        self.log_print("info", msg, to_screen)
    def lp_warning(self, msg, to_screen=True):
        self.log_print("warning", msg, to_screen)
    def lp_error(self, msg, to_screen=True):
        self.log_print("error", msg, to_screen)

# keep file names standard
def blob_name_(task_name : str, batch_id : int, file_type="json"):
    return f'{task_name}/{datetime.utcnow().isoformat()}/{batch_id}.{file_type}'

def upload_(destination_blob_name : str, source_object : dict, bucket_name=BUCKET_NAME):
    """Uploads object to the bucket.
    
    Parameters
    ----------
    destination_blob_name : str
        name of blob to upload in blob_name format
    source_object : dict {"type" : ["string", "file"], "data" : <any object>}
        type and data to upload

    Returns
    -------
    val if has value, else alt
    
    """
    if not (source_object.get("type") and source_object.get("data")):
        return {
            "status" : 1,
            "error" : 'Ill-formed source object. Expecting {"type" : ["string", "file"], "data" : <any object>}'
        }
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    try:
        if source_object["type"]=="string":
            blob.upload_from_string(source_object["data"])
        elif source_object["type"]=="file":
            blob.upload_from_filename(source_object["data"])
        return {"status" : 0}
    except Exception as E:
        return {
            "status" : 1,
            "error" : f'{E}'
        }

def common_log_(module, source_object_name):
    upload_(
        blob_name_(module, "common", "log"),
        source_object={"type" : "string", "data" : f'Uploaded {source_object_name}'},
        bucket_name=LOGGING_BUCKET_NAME
    )
