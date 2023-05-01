from decouple import config
from datetime import datetime
from google.cloud import storage

BUCKET_NAME = config("BUCKET_NAME", default="data-ingest-bk")
LOGGING_BUCKET_NAME = config("LOGGING_BUCKET_NAME", default="logging-bktasks")

storage_client = storage.Client()

def list_buckets():
    """Lists all buckets."""
    buckets = storage_client.list_buckets()
    return list(buckets)

def bucket_meta(bucket_name):
    """Prints out a bucket's metadata."""
    bucket = storage_client.get_bucket(bucket_name)
    return {
        "ID": {bucket.id},
        "Name": {bucket.name},
        "Storage Class": {bucket.storage_class},
        "Location": {bucket.location},
        "Location Type": {bucket.location_type},
        "Cors": {bucket.cors},
        "Default Event Based Hold": {bucket.default_event_based_hold},
        "Default KMS Key Name": {bucket.default_kms_key_name},
        "Metageneration": {bucket.metageneration},
        "Uniform Access": {bucket.iam_configuration["uniformBucketLevelAccess"]["enabled"]},
        "Public Access Prevention": {bucket.iam_configuration["publicAccessPrevention"]},
        "Retention Effective Time": {bucket.retention_policy_effective_time},
        "Retention Period": {bucket.retention_period},
        "Retention Policy Locked": {bucket.retention_policy_locked},
        "Requester Pays": {bucket.requester_pays},
        "Self Link": {bucket.self_link},
        "Time Created": {bucket.time_created},
        "Versioning Enabled": {bucket.versioning_enabled},
        "Labels": {bucket.labels}
    }

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
