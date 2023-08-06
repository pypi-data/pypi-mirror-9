from os.path import abspath, dirname, join
try:
  # try to use setuptools
  from setuptools import setup
  setupArgs = dict(
      include_package_data=True,
      install_requires=[
        "ZODB3",
        "setuptools", # to make `buildout` happy
      ] ,
      namespace_packages=['dm', 'dm.zodbpatches'],
      zip_safe=False,
      )
except ImportError:
  # use distutils
  from distutils import setup
  setupArgs = dict(
    )

cd = abspath(dirname(__file__))
pd = join(cd, 'dm', 'zodbpatches', 'commit_savepoint')

def pread(filename, base=pd): return open(join(base, filename)).read().rstrip()

setup(name='dm.zodbpatches.commit_savepoint',
      version=pread('VERSION.txt').split('\n')[0],
      description="Patch ZODB to work around https://github.com/zopefoundation/ZODB3/issues/2",
      long_description=pread('README.txt'),
      classifiers=[
#        'Development Status :: 3 - Alpha',
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Framework :: ZODB',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities',
        ],
      author='Dieter Maurer',
      author_email='dieter@handshake.de',
      url='http://pypi.python.org/pypi/dm.zodbpatches.commit_savepoint',
      packages=['dm', 'dm.zodbpatches', 'dm.zodbpatches.commit_savepoint'],
      keywords='ZODB patch',
      license='ZPL',
      **setupArgs
      )
