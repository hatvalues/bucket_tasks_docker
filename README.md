# bucket_tasks_docker

A Docker container for running generic upload/download tasks against GCP Cloud Storage

### Usage

#### CLI bucket_upload

usage: BucketUpload [-h] -f FILE_NAME -d DESTINATION_FOLDER [-b BUCKET] [-g LOGGING_BUCKET] [-c] [-j] [--header-row HEADER_ROW] [--headers HEADERS] [--batch-id BATCH_ID]

Convenience CLI Application For Uploading Files to Cloud Storage

optional arguments:
  -h, --help            show this help message and exit
  -f FILE_NAME, --file-name FILE_NAME
                        File or folder to upload. Supported types: csv, json, txt
  -d DESTINATION_FOLDER, --destination-folder DESTINATION_FOLDER
  -b BUCKET, --bucket BUCKET
  -g LOGGING_BUCKET, --logging-bucket LOGGING_BUCKET
  -c, --clear-log       Clear previous log?
  -j, --to-json         Upload object as json?
  --header-row HEADER_ROW
                        Which row contains headers. If no headers in file, set 0 and require --headers
  --headers HEADERS     Csv file has headers?
  --batch-id BATCH_ID   Batch id for upload

See Also bucket_downLoad -h

