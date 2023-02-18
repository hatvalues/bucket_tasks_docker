import os
from google.cloud import storage
from datetime import datetime

GCS_PROJECT_ID = os.getenv("DATASTORE_PROJECT_ID", "hatvalues-sandbox")
BUCKET_NAME = os.getenv("BUCKET_NAME", "data-ingest-bk")
LOGGING_BUCKET_NAME = os.getenv("LOGGING_BUCKET_NAME", "logging-bktasks")
GCS_PROJECT_ID = os.getenv("DATASTORE_PROJECT_ID")

storage_client = storage.Client()

# keep file names standard
def blob_name_(task_name : str, batch_id : int, file_type="json"):
    return f'{task_name}/{datetime.utcnow().isoformat()}/{batch_id}.{file_type}'

def upload_(destination_blob_name : str, source_object : dict, bucket_name=BUCKET_NAME):
    """Uploads object to the bucket."""
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    if source_object["type"]=="string":
        blob.upload_from_string(source_object["name"])
    elif source_object["type"]=="file":
        blob.upload_from_filename(source_object["name"])
