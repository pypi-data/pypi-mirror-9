from distutils.core import setup

setup(name='immaterial-digital-labor',
      author='Thomas Levine',
      author_email='_@thomaslevine.com',
      description='Stuff related to the Immaterial Digital Labor group',
      url='http://thomaslevine.com',
      install_requires = ['vlermv', 'requests'],
      tests_require = ['nose'],
      packages = ['archive', 'present'],
      entry_points={'console_scripts': [
          'immaterial-digital-labor-archive = archive:cli',
          'immaterial-digital-labor-html = present:main',
      ]},
      version='0.1',
      license='AGPL',
      classifiers=[
          'Programming Language :: Python :: 3.4',
      ],
)
