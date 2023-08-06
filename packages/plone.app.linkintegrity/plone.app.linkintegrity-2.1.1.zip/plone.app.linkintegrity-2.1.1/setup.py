from setuptools import setup, find_packages

version = '2.1.1'

setup(name='plone.app.linkintegrity',
      version=version,
      description='Manage link integrity in Plone.',
      long_description='\n\n'.join([
          open("README.rst").read(),
          open('CHANGES.rst').read(),
      ]),
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          "Environment :: Web Environment",
          "Framework :: Plone",
          "Framework :: Zope2",
          "Intended Audience :: Other Audience",
          "Intended Audience :: System Administrators",
          "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
          "Topic :: Internet :: WWW/HTTP :: Site Management :: Link Checking",
      ],
      keywords='link integrity plone',
      author='Plone Foundation',
      author_email='plone-developers@lists.sourceforge.net',
      url='http://pypi.python.org/pypi/plone.app.linkintegrity',
      license='GPL version 2',
      packages=find_packages(),
      namespace_packages=['plone', 'plone.app'],
      include_package_data=True,
      install_requires=[
          'setuptools',
          'plone.app.referenceablebehavior',  # Requires Products.Archetypes
      ],
      extras_require={
          'test': [
              'plone.app.testing',
              'plone.app.contenttypes',
              'plone.app.dexterity [relations]',  # related items in dx 2.0
          ],
      },
      platforms='Any',
      zip_safe=False,
      entry_points='''
        [z3c.autoinclude.plugin]
        target = plone
      ''',
      )
