
SETUP_INFO = dict(
    name = 'infi.logging',
    version = '0.4.4',
    author = 'Guy Rozendorn',
    author_email = 'guy@rzn.co.il',

    url = 'https://github.com/Infinidat/infi.logging',
    license = 'PSF',
    description = """Extensions for logbook, such as Windows EventLog handler.""",
    long_description = """Extensions for logbook, such as Windows EventLog handler.""",

    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers = [
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Python Software Foundation License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],

    install_requires = ['infi.registry', 'Logbook',	'setuptools'],
    namespace_packages = ['infi'],

    package_dir = {'': 'src'},
    package_data = {'': ['*dll']},
    include_package_data = True,
    zip_safe = False,

    entry_points = dict(
        console_scripts = [],
        gui_scripts = [],
        infi_logging_formatter_plugins = [
'channel = infi.logging.plugins.channel:ChannelFormatterPlugin',
'log_level = infi.logging.plugins.log_level:LogLevelFormatterPlugin',
'message = infi.logging.plugins.message:MessageFormatterPlugin',
'hostname = infi.logging.plugins.hostname:HostNameFormatterPlugin',
'greenlet_id = infi.logging.plugins.greenlet_id:GreenletIDFormatterPlugin',
'procname = infi.logging.plugins.procname:ProcnameFormatterPlugin',
'request_id_tag = infi.logging.plugins.request_id_tag:RequestIDTagFormatterPlugin',
'process_id = infi.logging.plugins.process_id:ProcessIDFormatterPlugin',
'thread_id = infi.logging.plugins.thread_id:ThreadIDFormatterPlugin',
'time = infi.logging.plugins.time:TimeFormatterPlugin'],
        infi_logging_injector_plugins = [
'hostname = infi.logging.plugins.hostname:HostNameInjectorPlugin',
'greenlet_id = infi.logging.plugins.greenlet_id:GreenletIDInjectorPlugin',
'procname = infi.logging.plugins.procname:ProcnameInjectorPlugin',
'request_id_tag = infi.logging.plugins.request_id_tag:RequestIDTagInjectorPlugin',
'thread_id = infi.logging.plugins.thread_id:ThreadIDInjectorPlugin']
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

