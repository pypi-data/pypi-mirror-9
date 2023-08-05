from distutils.core import setup

setup(name='io-whois',
      author='Thomas Levine',
      author_email='_@thomaslevine.com',
      description='Download WHOIS data for popular .io domains',
      url='https://small.dada.pink/io-whois',
      install_requires = ['vlermv','requests','lxml'],
      py_modules=['whois'],
      entry_points={'console_scripts': ['io-whois = whois:main']},
      version='0.0.2',
      license='AGPL',
)
