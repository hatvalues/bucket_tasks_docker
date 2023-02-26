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
    epilog = "See Also bucket_downLoad -h"
)
arg_parser.add_argument("-f", "--file-name", required=True, help="File or folder to upload. Supported types: csv, json, txt")
arg_parser.add_argument("-b", "--bucket", default=BUCKET_NAME, help="Destination bucket")
arg_parser.add_argument("-d", "--destination-folder", default="/")
arg_parser.add_argument("-g", "--logging-bucket", default=LOGGING_BUCKET_NAME, help="Logging bucket")
arg_parser.add_argument(
    "-c", "--clear-log",
    action="store_true",
    help="Clear previous log?"
)
arg_parser.add_argument(
    "-j", "--to-json",
    action="store_true",
    help="Upload object as json?"
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

def args_d_parse_(destination_folder):
    if destination_folder=="/":
        return ""
    elif destination_folder[-1]!="/":
        destination_folder += "/"
    return destination_folder

if not (path.is_file() or path.is_dir()):
    lg.lp_error(f'INVALID FILE: -f/--file-name {args.file_name}')
    sys.exit()
if path.is_file():
    lg.lp_info(f'Opening file {args.file_name}')
    file_stem = path.stem
    file_destination = f'{args_d_parse_(args.destination_folder)}{file_stem}'
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
elif path.is_dir(): # folder
    lg.lp_info(f'Scanning contents of directory {args.file_name}')
    for p in path.rglob("*"):
        child_source_path = str(p)
        destination_folder = args_d_parse_(args.destination_folder)
        child_destination_path = child_source_path.replace(f'{args.file_name}/', "")
        child_destination_path = f'{destination_folder}{child_destination_path}'
        source_object = {
            "type" : "file",
            "data" : child_source_path
        }
        lg.lp_info(f'Uploading {child_source_path} to {child_destination_path}')
        upload_(
            f'{destination_folder}{child_destination_path}',
            source_object=source_object,
            bucket_name=args.bucket
        )
    lg.lp_info(f'Uploading common log')
    common_log_("bucket_upload", f'Uploaded all files from path walk at {args.file_name}')        
else: # not valid?
    lg.lp_error(f'{FileNotFoundError(args.file_name)}')


lg.lp_info(f'JOB FINISHED')

