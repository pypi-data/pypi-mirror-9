from setuptools import setup

files = ['docs/*']
setup(
        name = 'network_meeting_example_karl',
        version = '2.0.501',
        description = 'this is a short de',
        author = 'Karl Krieser',
        url = 'tbd',
        packages = ['rogers'],
        package_data = {'package': files},
        entry_points = {
                       'console_scripts':[
                                          'rogers = rogers.neighborhood:smain'
                                          ]
                       },
        scripts = ['runner_for_rogers'],
        long_description = 'this is a much longer description than you would initially guess',
        classifiers = ['Programming Language :: Python', \
                     'Programming Language :: Python :: 3', \
                     'Operating System :: Unix', \
                     'Development Status :: 1 - Planning', \
                     'Intended Audience :: Science/Research', \
                     'Topic :: Scientific/Engineering :: Bio-Informatics', \
                     'License :: OSI Approved :: GNU General Public License v3 (GPLv3)', \
                     'Natural Language :: English']
       )
