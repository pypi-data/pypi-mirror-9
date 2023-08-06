# -*- coding: utf-8 -*-

""" This module is used for virtualenv relatives """

import fabtools
from fabric.api import env
from pydiploy.decorators import do_verbose


@do_verbose
def virtualenv(clear=False):
    """ Creates virtualenv """
    fabtools.require.files.directory(env.remote_virtualenv_dir,
                                     owner=env.remote_owner,
                                     group=env.remote_group,
                                     use_sudo=True)
    python_bin = '/usr/bin/python%s' % env.remote_python_version
    fabtools.require.python.virtualenv(env.remote_virtualenv_dir,
                                       user=env.remote_owner,
                                       clear=clear, use_sudo=True,
                                       venv_python=python_bin)
