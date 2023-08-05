from setuptools import setup

setup(name='smapp_collection_stats',
      version='0.1.0',
      description='NYU SMaPP lab utility library',
      author='NYU SMaPP',
      license='GPLv2',
      author_email='smapp_programmer-group@nyu.edu',
      url='http://smapp.nyu.edu',
      packages=['smapp_collection_stats'],
      install_requires=[
          'smapp_toolkit >= 0.1.13',
          'python-dateutil'
      ],
     )
