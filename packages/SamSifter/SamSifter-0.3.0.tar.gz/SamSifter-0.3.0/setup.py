# Work around mbcs bug in distutils.
# http://bugs.python.org/issue10945
import codecs
try:
    codecs.lookup('mbcs')
except LookupError:
    ascii = codecs.lookup('ascii')
    func = lambda name, enc=ascii: {True: enc}.get(name == 'mbcs')
    codecs.register(func)

from setuptools import setup

""" custom libraries """
from samsifter.version import samsifter_version


def readme():
    with open('README.rst') as f:
        return f.read()

setup(
    name='SamSifter',
#    version='0.3.0',
    version=samsifter_version,
    description='Workflow editor for metagenomic analysis',
    long_description=readme(),
    # see full list at https://pypi.python.org/pypi?:action=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: X11 Applications :: Qt',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Scientific/Engineering :: Bio-Informatics'
    ],
    url='http://www.biohazardous.de/samsifter',
    # to be published soon at:
#    url='http://pypi.python.org/pypi/SamSifter/',
    author='Florian Aldehoff',
    author_email='f.aldehoff@student.uni-tuebingen.de',
    license='LICENSE.txt',
    packages=[
        'samsifter',
        'samsifter.filters', 'samsifter.gui', 'samsifter.models',
        'samsifter.resources', 'samsifter.util', 'samsifter.views',
        'samsifter.stats', 'pmdtools'
    ],
    scripts=['bin/enrich_summary'],
    entry_points={
        'console_scripts': [
            'calculate_pmds=samsifter.filters.calculate_pmds:main',
            'compile_stats=samsifter.stats.compile_stats:main',
            'count_taxon_reads=samsifter.filters.count_taxon_reads:main',
            'filter_read_conservation=samsifter.filters.filter_read_conservation:main',
            'filter_read_list=samsifter.filters.filter_read_list:main',
            'filter_ref_coverage=samsifter.filters.filter_ref_coverage:main',
            'filter_ref_identity=samsifter.filters.filter_ref_identity:main',
            'filter_ref_list=samsifter.filters.filter_ref_list:main',
            'filter_ref_pmds=samsifter.filters.filter_ref_pmds:main',
            'filter_taxon_list=samsifter.filters.filter_taxon_list:main',
            'filter_taxon_pmds=samsifter.filters.filter_taxon_pmds:main',
            'pmdtools_mod=pmdtools.pmdtools_0_55_mod:main',
            'summarize_stats=samsifter.stats.summarize_stats:main'
        ],
        'gui_scripts': [
            'samsifter=samsifter.samsifter:main'
        ]
    },
	data_files=[
		('/usr/local/share/icons/hicolor/scalable/apps', ['samsifter/resources/images/samsifter.svg']),
		('/usr/local/share/applications', ['samsifter/resources/samsifter.desktop'])
	],
    install_requires=[
#        'PyQt == 4.11.2',     # unfortunately not available on PyPI
#        'matplotlib >= 1.1',
        'matplotlib >= 1.3.1',
        'pandas >= 0.14.1',     # already requires numpy as well...
        'numpy >= 1.6.1',
#        'numpy == 1.8.2',
    ],
    zip_safe=False
)
