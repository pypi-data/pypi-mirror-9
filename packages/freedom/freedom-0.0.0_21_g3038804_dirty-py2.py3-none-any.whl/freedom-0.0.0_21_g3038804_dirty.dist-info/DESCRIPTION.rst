# README #

A python release management tool.

[ ![Codeship Status for sys-git/freedom](https://codeship.com/projects/7abb60f0-7d41-0132-fcd7-6602ec740206/status?branch=master)](https://codeship.com/projects/56601)
[![Build Status](https://api.shippable.com/projects/54b500d45ab6cc135288711c/badge?branchName=master)](https://app.shippable.com/projects/54b500d45ab6cc135288711c/builds/latest)

* Version 0.0.1

### How do I get set up? ###

* **python setup.py install**
* Run the tests from source **python setup.py nosetests**
* Dependencies:  None
* How to run tests with all nosetests options set:  **./runtests.sh**
* Deployment instructions (coming soon):  **pip install freedom**



### Requirements ###

At least Python 2.6
Tested on Python 2.7, 3.4.0

### Contribution guidelines ###

I accept pull requests.

### Who do I talk to? ###

* Francis Horsman:  **francis.horsman@gmail.com**

### Example ###

```
>>> python release.py --help

Usage: release.py [OPTIONS]

Options:
  --verbose                 Enabled more verbose output.
  --tag                     tag this release
  --build_release                   build_release this release
  --publish_release                 publish_release to pypi
  --dryrun                  Perform a dry-run (no side effects in git or pypi)
  --profile-env TEXT        Environmental variable which holds profile
                            information in, defaults to RELEASEME_PROFILE.
  --profile TEXT            Load options from this profile file (overrides all
                            other options).
  --history-version TEXT    New version (optional - previous version will be
                            incremented).
  --history-date TEXT       The date to use in the history synopsis when
                            tagging a release.
  --history-comment TEXT    The changelog comment to add.
  --history-file TEXT       The history text file to use.
  --history-delimiter TEXT  The history file synopsis delimiter (just prior to
                            history entries).
  --history-meta TEXT       The history file synopsis (prior to the
                            delimiter).
  --git-profile TEXT        Load options from this git profile file (overrides
                            all other options)
  --git-repo TEXT           Location of the git repo to release (defaults to
                            cwd: /home/francis/PycharmProjects/freedom)
  --help                    Show this message and exit.

```

.. :changelog:

Changelog
=========



