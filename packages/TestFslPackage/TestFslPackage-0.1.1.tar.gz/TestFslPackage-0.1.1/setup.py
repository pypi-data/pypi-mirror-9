from distutils.core import setup

setup(
   name='TestFslPackage',
   version='0.1.1',
   author='Trinath Somanchi',
   author_email='trinath.somanchi@freescale.com',
   packages=['fake-fsl-pkg', 'fake-fsl-pkg.test'],
   scripts=['bin/fake-fsl.py'],
   url='http://pypi.python.org/pypi/TestFslPackage',
   license='LICENSE',
   description='Fake Pypi Package - Hello World.',
   long_description=open('README').read(),
   )
