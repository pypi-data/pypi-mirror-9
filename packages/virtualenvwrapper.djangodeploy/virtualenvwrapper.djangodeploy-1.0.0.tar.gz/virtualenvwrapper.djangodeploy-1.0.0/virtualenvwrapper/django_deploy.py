#!/usr/bin/env python
# encoding: utf-8
#
# Copyleft Tino de Bruijn. No rights reserved.
#
"""
Create a directory structure for deploying django websites automatically with virtualenvwrapper.
"""

import logging
import os
import subprocess

log = logging.getLogger('virtualenvwrapper.djangodeploy')


def template(args):
    """
    Makes directories: code, conf, log, media and static
    Install envdir and create code/.env/DJANGO_SETTINGS_MODULE
    (with contents "{project}.settings.production")
    """
    project, project_dir = args
    os.chdir(project_dir)
    for dir in ('code', 'conf', 'log', 'media', 'static'):
        try:
            os.mkdir(dir)
        except OSError as e:
            if e.errno != 17:  # Dir already exists
                raise e
    return
