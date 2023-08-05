"""Build, install, clean package using setup.py"""


from __future__ import print_function, division

from . import _setup_build
from . import _setup_install
from . import _setup_clean

def main():
    """run _setup_build, _setup_install, _setup_clean"""

    print('Build, install, clean.')
    _setup_build.main()
    _setup_install.main()
    _setup_clean.main()


if __name__ == '__main__':
    main()
