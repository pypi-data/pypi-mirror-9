from setuptools import setup

files = ['input/*', 'out/*']

setup(
      name = 'west_enrich',
      version = '1',
      description = 'Local enrichment of cluster files (GO/OMIM)',
      author = 'Sean West',
      url = 'tbd',
      packages = ['enrich'],
      package_data = {'package' : files},
      entry_points = {
                      'console_scripts':[
                                         'west_enrich = enrich.central_hub:smain'
                                         ]
                      },
      scripts = ['run_enrich'],
      long_description = 'long description',
      classifiers = ['Programming Language :: Python', \
                     'Programming Language :: Python :: 3', \
                     'Operating System :: Unix', \
                     'Development Status :: 1 - Planning', \
                     'Intended Audience :: Science/Research', \
                     'Topic :: Scientific/Engineering :: Bio-Informatics', \
                     'Topic :: Scientific/Engineering :: Mathematics', \
                     'License :: OSI Approved :: GNU General Public License v3 (GPLv3)', \
                     'Natural Language :: English']
      )