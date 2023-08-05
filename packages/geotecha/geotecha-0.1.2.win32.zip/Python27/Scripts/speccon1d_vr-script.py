#!C:\Python27\python.exe
# EASY-INSTALL-ENTRY-SCRIPT: 'geotecha==0.1.2','console_scripts','speccon1d_vr'
__requires__ = 'geotecha==0.1.2'
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.exit(
        load_entry_point('geotecha==0.1.2', 'console_scripts', 'speccon1d_vr')()
    )
