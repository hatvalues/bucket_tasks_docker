from utilities import BUCKET_NAME, LOGGING_BUCKET_NAME
from utilities import StandardLogger
from utilities import upload_, blob_name_, common_log_
from file_utilities import preproc_csv
from pathlib import Path
import argparse
import sys
import json

arg_parser = argparse.ArgumentParser(
    prog = "BucketUpload",
    description = "Convenience CLI Application For Uploading Files to Cloud Storage",
    epilog = "See Also BucketDownLoad -h"
)
arg_parser.add_argument("-f", "--file-name", required=True, help="File or folder to upload. Supported types: csv, json, txt")
arg_parser.add_argument("-d", "--destination-folder", required=True)
arg_parser.add_argument("-b", "--bucket", default=BUCKET_NAME)
arg_parser.add_argument("-g", "--logging-bucket", default=LOGGING_BUCKET_NAME)
arg_parser.add_argument(
    "-c", "--clear-log",
    action="store_true",
    help="Clear previous log?"
)
arg_parser.add_argument(
    "-j", "--to-json",
    action="store_true",
    help="Convert to json before uploading?"
)
arg_parser.add_argument(
    "--header-row",
    default="1",
    help="Which row contains headers. If no headers in file, set 0 and require --headers"
)
arg_parser.add_argument(
    "--headers",
    default="1",
    help="Csv file has headers?"
)
arg_parser.add_argument(
    "--batch-id",
    default="1",
    help="Batch id for upload"
)

args = arg_parser.parse_args()

lg = StandardLogger(arg_parser.prog)
if args.clear_log:
    lg.clear_log()
lg.lp_info("LOGGER OPENED")
try:
    header_row = int(args.header_row)
except ValueError:
    lg.lp_error(f'Invalid --header-row argument. Expected integer-like')
    sys.exit()

lg.lp_info(f'JOB STARTING')
path = Path(args.file_name)
if not path.is_file() or path.is_dir():
    lg.lp_error(f'INVALID FILE: -f/--file-name {args.file_name}')
    sys.exit()
if path.is_file():
    lg.lp_info(f'Opening file {args.file_name}')
    file_stem = path.stem
    file_destination = f'{args.destination_folder}/{file_stem}'
    file_type = path.suffix.replace(".", "")
    if args.to_json:
        lg.lp_info(f'Converting {file_type} to json')
        if file_type=="csv":
            # TODO: no header row
            data = preproc_csv(args.file_name, header_row)
        source_object = {
            "type" : "string",
            "data" : json.dumps(data)
        }
        file_type = "json"
    else: # upload file as is
        source_object = {
            "type" : "file",
            "data" : args.file_name
        }
    lg.lp_info(f'Uploading data from source {args.file_name} to destination {file_destination}')
    upload_(
        blob_name_(file_destination, args.batch_id, file_type),
        source_object=source_object,
        bucket_name=args.bucket
    )
    lg.lp_info(f'Uploading common log')
    common_log_("bucket_upload", f'{args.file_name} as {file_type}')
else: # folder
    # TODO
    pass

lg.lp_info(f'JOB FINISHED')

