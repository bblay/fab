#!/usr/bin/env python
import os
import sys
from os import getcwd


print("\n--- grab_gcom.py ---\n")

print("sys.path", sys.path)
print("cwd", getcwd())
print("exe", sys.executable)
print("user", os.getlogin())
print("node", os.uname()[1])

# print('CONDA_DEFAULT_ENV', os.environ['CONDA_DEFAULT_ENV'])


from fab.build_config import BuildConfig
from gcom_build_common import grab_step


def gcom_source_config():
    """
    Grab the gcom source, for use by multiple rose build configs.

    """
    return BuildConfig(label='gcom source', steps=[grab_step()])


if __name__ == '__main__':
    print("__main__")
    gcom_source_config().run()
