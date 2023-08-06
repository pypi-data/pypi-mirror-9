from distutils.core import setup
setup(
      name = 'minchash',
      packages = ['minchash'],
      version = '0.1',
      description = 'Multi-set Incremental Hash',
      author = 'Mikael Sanchez',
      author_email = 'keyneom122@hotmail.com',
      url = 'https://bitbucket.org/keyneom/minchash',
      download_url = 'https://bitbucket.org/keyneom/minchash/get/0.1.tar.bz2',
      keywords = ['hash', 'incremental', 'multiset'],
      classifiers = [],
      license='MIT',
      install_requires=['gmpy']
)
