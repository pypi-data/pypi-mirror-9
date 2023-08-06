from setuptools import setup, find_packages
from os.path import join

name = 'plone.app.imaging'
readme = open("README.rst").read()
history = open(join('docs', 'HISTORY.txt')).read()

setup(name = name,
      version='1.1.3',
      description = 'User-configurable, blob-aware image scaling for Plone.',
      long_description = readme[readme.find('\n\n'):] + '\n' + history,
      classifiers=[
          "Environment :: Web Environment",
          "Framework :: Plone",
          "Framework :: Plone :: 5.0",
          "Framework :: Zope2",
          'Intended Audience :: Developers',
          'Intended Audience :: Other Audience',
          'Intended Audience :: System Administrators',
          "License :: OSI Approved :: GNU General Public License (GPL)",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.7",
        ],
      keywords='images scaling zodb blob plone',
      author='Plone Foundation',
      author_email='plone-developers@lists.sourceforge.net',
      url='http://pypi.python.org/pypi/plone.app.imaging',
      license='GPL version 2',
      packages = find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages = ['plone', 'plone.app'],
      include_package_data = True,
      install_requires = [
        'setuptools',
        'plone.app.controlpanel',
        'plone.scale [storage]',
        'Products.Archetypes',
        'z3c.caching',
        'five.globalrequest'
      ],
      extras_require = {'test':
          ['plone.app.testing',
           'Products.ATContentTypes' ]},
      platforms = 'Any',
      zip_safe = False,
      entry_points = '''
        [z3c.autoinclude.plugin]
        target = plone
      ''',
)
