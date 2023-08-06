from setuptools import setup

setup(name='Google-Search-API',
      version='1.1.1',
      url='https://github.com/abenassi/Google-Search-API',
      description='Search in google',
      author='Anthony Casagrande, Agustin Benassi',
      author_email='birdapi@gmail.com, agusbenassi@gmail.com',
      license='MIT',

      packages=['google'],

      setup_requires=['nose>=1.0'],
      test_suite='nose.collector',
      tests_require=['nose', 'nose-cov']
      )
