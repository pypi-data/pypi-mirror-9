import datetime
import os
import re

class ConfigDirectory(object):
  def just_files(self, names):
    return filter(os.path.isfile, names)

  def get_files_in_directory(self, dirname):
    contents = os.listdir(dirname)
    def add_path(filename):
      return os.path.join(dirname, filename)
    contents = map(add_path, contents)
    return self.just_files(contents)

  def is_pipeline_conf(self, name):
    pattern = re.compile('.+_pipeline.conf$')
    match = pattern.match(name)
    return match != None

  def find_job_trackers_in_folder(self, dirname):
    files = self.get_files_in_directory(dirname)
    job_trackers = filter(self.is_pipeline_conf, files)
    return job_trackers

  def just_dirs(self, names):
    return filter(os.path.isdir, names)

  def get_subdirectories(self, parent):
    contents = os.listdir(parent)
    def add_path(child):
      return os.path.join(parent, child)
    contents = map(add_path, contents)
    return self.just_dirs(contents)

  def get_all_job_tracker_filenames(self, dirname):
    job_trackers = self.find_job_trackers_in_folder(dirname)
    child_directories = self.get_subdirectories(dirname)
    for child_directory in child_directories:
      job_trackers += self.find_job_trackers_in_folder(child_directory)
    return job_trackers

  def get_job_trackers(self, dirname):
    job_tracker_filenames = self.get_all_job_tracker_filenames(dirname)
    return [TrackerFile(filename) for filename in job_tracker_filenames]

  def to_dict(self, dirname):
    jobs = []
    for tracker in self.get_job_trackers(dirname):
      for job in tracker.get_jobs():
        jobs.append({ 'approval_required': job.approval_required,
                      'job_type': job.job_type,
                      'config_file': job.config_file,
                      'pipeline_tracker': tracker.path })
    return { 'jobs': jobs, 'created_at': datetime.datetime.now().isoformat() }

class TrackerFile(object):
  def __init__(self, path):
    self.path = path

  def get_lines(self):
    with open(self.path, 'r') as tracker_file:
      contents = tracker_file.read().strip('\n')
    return contents.split('\n')

  def get_jobs(self):
    jobs = []
    for line in self.get_lines():
      try:
        jobs.append(PipelineJob(line))
      except ValueError:
        pass # Could not parse line in file, ignoring
    return jobs


class PipelineJob(object):
  def __init__(self, config_line):
    self.config_line = config_line
    self.approval_required = self.is_approval_required(config_line)
    self.job_type = self.get_job_type(config_line)
    self.config_file = self.get_job_config(config_line)
    if not(self.job_type and self.config_file):
      raise ValueError("Could not parse job details from '%s'" % config_line)

  def is_approval_required(self, line):
    pattern = re.compile('^#admin_approval_required#')
    return pattern.match(line) != None

  def get_job_type(self, line):
    pattern = re.compile('^(#admin_approval_required#)?\s*(__.*__)\s')
    matches = pattern.match(line)
    if matches == None:
      return None
    else:
      return matches.groups()[1]

  def get_job_config(self, line):
    pattern = re.compile('^(#admin_approval_required#)?\s*(__.*__)\s*([^#\s]+)\s*($|#)')
    matches = pattern.match(line)
    if matches == None:
      return None
    else:
      return matches.groups()[2]
