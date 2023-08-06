from setuptools import setup

setup(name='receptive',
      version='1.2',
      description='Receptive integration for Python',
      url='https://github.com/Receptive/receptive-python',
      author='Dan Dukeson',
      author_email='dan@receptive.io',
      license='MIT',
      packages=['receptive'],
      test_suite='nose.collector',
      tests_require=['nose'],
      zip_safe=False)

