from dotenv import load_dotenv
import os

GCS_PROJECT_ID = os.getenv("DATASTORE_PROJECT_ID", "hatvalues-sandbox")
BUCKET_NAME = os.getenv("BUCKET_NAME", "data-ingest-bk")
LOGGING_BUCKET_NAME = os.getenv("LOGGING_BUCKET_NAME", "logging-bktasks")

