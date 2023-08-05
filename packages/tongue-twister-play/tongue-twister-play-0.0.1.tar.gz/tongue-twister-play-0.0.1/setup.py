from distutils.core import setup

setup(name='tongue-twister-play',
      author='Thomas Levine',
      author_email='_@thomaslevine.com',
      description='Make a play of tongue twisters',
      url='http://small.dada.pink/tongue-twister-play',
      install_requires = ['vlermv','twister'],
      packages=['twistermap'],
      entry_points={'console_scripts': ['tongue-twister-play = twistermap:example']},
      version='0.0.1',
      license='AGPL',
)
