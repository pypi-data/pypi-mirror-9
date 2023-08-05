import os.path as osp
try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

# pip install -e .[develop]
develop_requires = [
    'BlazeWeb',
    # tests rely on SQL string comparison which fails with SA < 0.9
    'SQLAlchemy>=0.9.0'
    'SQLAlchemyBWC',
    'mock',
    'nose',
    'Flask',
    'Flask-Bootstrap',
    'Flask-SQLAlchemy',
    'Flask-WebTest',
    'wrapt',
    'xlrd',
    'xlwt',
]

cdir = osp.abspath(osp.dirname(__file__))
README = open(osp.join(cdir, 'readme.rst')).read()
CHANGELOG = open(osp.join(cdir, 'changelog.rst')).read()
VERSION = open(osp.join(cdir, 'webgrid', 'version.txt')).read().strip()

setup(
    name="WebGrid",
    version=VERSION,
    description="A library for rendering HTML tables and Excel files from SQLAlchemy models.",
    long_description='\n\n'.join((README, CHANGELOG)),
    author="Randy Syring",
    author_email="randy@thesyrings.us",
    url='https://bitbucket.org/rsyring/webgrid',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
    license='BSD',
    packages=['webgrid'],
    extras_require={'develop': develop_requires},
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        'BlazeUtils',
        'FormEncode',
        'jinja2',
        'SQLAlchemy',
        'webhelpers',
        'python-dateutil',
        'Werkzeug',
    ],
    entry_points="""
        [console_scripts]
        webgrid_ta = webgrid_ta.manage:script_entry

        [nose.plugins]
        webgridta_initapp = webgrid.webgrid_nose:WebGridNosePlugin
    """,
)

