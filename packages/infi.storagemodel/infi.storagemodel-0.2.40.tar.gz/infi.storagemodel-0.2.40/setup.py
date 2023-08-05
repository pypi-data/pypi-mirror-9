
SETUP_INFO = dict(
    name = 'infi.storagemodel',
    version = '0.2.40',
    author = 'Guy Rozendorn',
    author_email = 'guy@rzn.co.il',

    url = 'https://github.com/Infinidat/infi.storagemodel',
    license = 'PSF',
    description = """A high-level library for traversing the OS storage model.""",
    long_description = """A high-level cross-platform abstraction of the OS storage stack (LUNs, disks, volumes, etc).""",

    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers = [
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Python Software Foundation License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],

    install_requires = [
'Brownie>=0.5.1',
'daemon>=1.0',
'infi.asi>=0.3.27',
'infi.cwrap>=0.2.9',
'infi.devicemanager>=0.2.11',
'infi.diskmanagement>=0.3.5',
'infi.dtypes.hctl>=0.0.7',
'infi.dtypes.wwn>=0.1',
'infi.exceptools>=0.2.7',
'infi.hbaapi>0.1.21',
'infi.instruct>=0.6.25',
'infi.mountoolinux>=0.1.15',
'infi.multipathtools>=0.1.28',
'infi.parted>=0.2.4',
'infi.pyutils>=1.0.8',
'infi.sgutils>=0.1.7',
'infi.traceback>=0.3.10',
'infi.wioctl>=0.1.8',
'infi.wmpio>=0.1.22',
'setuptools>=5.4.1'
],
    namespace_packages = ['infi'],

    package_dir = {'': 'src'},
    package_data = {'': []},
    include_package_data = True,
    zip_safe = False,

    entry_points = dict(
        console_scripts = ['devlist = infi.storagemodel.examples:devlist', 'rescan_scsi_bus = infi.storagemodel.linux.rescan_scsi_bus:console_script'],
        gui_scripts = [],
        ),
)

if SETUP_INFO['url'] is None:
    _ = SETUP_INFO.pop('url')

def setup():
    from setuptools import setup as _setup
    from setuptools import find_packages
    SETUP_INFO['packages'] = find_packages('src')
    _setup(**SETUP_INFO)

if __name__ == '__main__':
    setup()

