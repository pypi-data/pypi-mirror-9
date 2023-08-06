Pathogen Pipeline Configuration Tools (path\_pipe\_conf\_tools)
===============================================================

This is probably not very interesting unless you work in the pathogen
informatics team at the Wellcome Trust Sanger Institute and almost
certainly not it you don't use `the vr-pipe
pipeline <https://github.com/VertebrateResequencing/vr-pipe>`_.

Given a config directory, this script finds all of the
``*_pipeline.conf`` files in the directory and its immediate children.
It parses these files and outputs their contents in json. This is either
saved to a file or stdout.

This is used in collaboration with
`jsontoemail <https://github.com/sanger-pathogens/jsontoemail>`_ and a
``cron`` job to send updates / reminders to the pathogen informatics
team.

Usage
-----

::

    $ list-pathogen-pipeline-jobs -h
    usage: list-pathogen-pipeline-jobs [-h] [--output_file OUTPUT_FILE] config_dir

    Outputs details of all of the pathogen jobs in the pipeline

    positional arguments:
      config_dir            Config directory to be searched for job trackers (also
                            searches child dircectories)

    optional arguments:
      -h, --help            show this help message and exit
      --output_file OUTPUT_FILE, -o OUTPUT_FILE
                            File to output results to (defaults to stdout)

Example output
--------------

::

    {
      "created_at": "2015-03-24T15:26:17.246253",
      "jobs": [
        {
          "approval_required": true,
          "config_file": "/parent_dir/assembly_jobs/job_1.conf",
          "job_type": "__Assembly__",
          "pipeline_tracker": "/parent_dir/assembly_job_tracker.conf"
        },
        {
          "approval_required": true,
          "config_file": "/parent_dir/assembly_jobs/job_2.conf",
          "job_type": "__Assembly__",
          "pipeline_tracker": "/parent_dir/assembly_job_tracker.conf"
        },
        {
          "approval_required": false,
          "config_file": "/parent_dir/assembly_jobs/job_3.conf",
          "job_type": "__Assembly__",
          "pipeline_tracker": "/parent_dir/assembly_job_tracker.conf"
        },
        {
          "approval_required": true,
          "config_file": "/parent_dir/annotation_jobs/job_1.conf",
          "job_type": "__Annotation__",
          "pipeline_tracker": "/parent_dir/annotation_job_tracker.conf"
        },
        {
          "approval_required": false,
          "config_file": "/parent_dir/mapping_jobs/job_1.conf",
          "job_type": "__Mapping__",
          "pipeline_tracker": "/parent_dir/mapping_job_tracker.conf"
        },
        {
          "approval_required": false,
          "config_file": "/parent_dir/mapping_jobs/job_2.conf",
          "job_type": "__Mapping__",
          "pipeline_tracker": "/parent_dir/mapping_job_tracker.conf"
        }
      ]
    }

Testing
-------

::

    ./run_tests.sh

Dependencies
------------

Tests require: 

- mock

path\_pipe\_conf\_tools has been tested on Ubuntu 12.04 with python
2.7.3
