from glob import glob
from setuptools import setup, find_packages
setup(name = 'worch-ups',
      version = '0.5.0',
      description = 'Worch/waf tools and features for working with UPS.',
      author = 'Brett Viren',
      author_email = 'brett.viren@gmail.com',
      license = 'GPLv2',
      url = 'http://github.com/brettviren/worch-ups',
      namespace_packages = ['worch'],
      packages = ['worch','worch.upstools'],
      install_requires = [l for l in open("requirements.txt").readlines() if l.strip()],
      data_files = [('share/worch/config/examples', glob('examples/*.cfg')),],
)

