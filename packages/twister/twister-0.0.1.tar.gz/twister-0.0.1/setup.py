from distutils.core import setup

setup(name='twister',
      author='Thomas Levine',
      author_email='_@thomaslevine.com',
      description='Download tongue twisters',
      url='https://small.dada.pink/twister',
      install_requires = ['vlermv','requests','lxml'],
      py_modules=['twister'],
      entry_points={'console_scripts': ['twister = twister:main']},
      version='0.0.1',
      license='AGPL',
)
