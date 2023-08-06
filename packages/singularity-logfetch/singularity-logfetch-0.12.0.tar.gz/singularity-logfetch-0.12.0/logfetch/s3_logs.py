import os
import sys
import re
import grequests
import logfetch_base
from termcolor import colored
from callbacks import generate_callback
from singularity_request import get_json_response

TASK_FORMAT = '/task/{0}'
S3LOGS_URI_FORMAT = '{0}/logs{1}'
REQUEST_FORMAT = '/request/{0}'

def download_s3_logs(args):
  sys.stderr.write(colored('Checking for S3 log files', 'cyan') + '\n')
  logs = logs_for_all_requests(args)
  async_requests = []
  all_logs = []
  for log_file in logs:
    filename = log_file['key'].rsplit("/", 1)[1]
    if logfetch_base.is_in_date_range(args, time_from_filename(filename)):
      if not already_downloaded(args.dest, filename):
        async_requests.append(
          grequests.AsyncRequest('GET', log_file['getUrl'], callback=generate_callback(log_file['getUrl'], args.dest, filename, args.chunk_size))
        )
      all_logs.append('{0}/{1}'.format(args.dest, filename.replace('.gz', '.log')))
  if async_requests:
    sys.stderr.write(colored('Starting S3 Downloads', 'cyan'))
    grequests.map(async_requests, stream=True, size=args.num_parallel_fetches)
  zipped_files = ['{0}/{1}'.format(args.dest, log_file['key'].rsplit("/", 1)[1]) for log_file in logs]
  sys.stderr.write(colored('Unpacking S3 logs\n', 'cyan'))
  logfetch_base.unpack_logs(zipped_files)
  sys.stderr.write(colored('All S3 logs up to date', 'cyan') + '\n')
  return all_logs

def already_downloaded(dest, filename):
  return (os.path.isfile('{0}/{1}'.format(dest, filename.replace('.gz', '.log'))) or os.path.isfile('{0}/{1}'.format(dest, filename)))

def logs_for_all_requests(args):
  if args.taskId:
    return get_json_response(s3_task_logs_uri(args, args.taskId))
  else:
    tasks = logfetch_base.tasks_for_requests(args)
    logs = []
    for task in tasks:
      s3_logs = get_json_response(s3_task_logs_uri(args, task))
      logs = logs + s3_logs if s3_logs else logs
    sys.stderr.write(colored('Also searching s3 history...\n', 'magenta'))
    for request in logfetch_base.all_requests(args):
      s3_logs = get_json_response(s3_request_logs_uri(args, request))
      logs = logs + s3_logs if s3_logs else logs
    return [dict(t) for t in set([tuple(l.items()) for l in logs])]

def time_from_filename(filename):
  time_string = re.search('(\d{13})', filename).group(1)
  return int(time_string[0:-3])

def s3_task_logs_uri(args, idString):
  return S3LOGS_URI_FORMAT.format(logfetch_base.base_uri(args), TASK_FORMAT.format(idString))

def s3_request_logs_uri(args, idString):
  return S3LOGS_URI_FORMAT.format(logfetch_base.base_uri(args), REQUEST_FORMAT.format(idString))

