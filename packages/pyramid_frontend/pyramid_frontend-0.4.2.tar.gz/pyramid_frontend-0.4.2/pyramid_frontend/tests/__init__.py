from __future__ import absolute_import, print_function, division

import os
import os.path
import shutil

from .utils import work_dir


def setup():
    if os.path.exists(work_dir):
        shutil.rmtree(work_dir)
    os.makedirs(work_dir)
