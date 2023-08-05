from setuptools import setup, find_packages

setup(name='qllauncher',
      packages=find_packages(),
      version='0.6.1.6',
      author='Victor Polevoy',
      author_email='contact@vpolevoy.com',
      url='https://bitbucket.org/fx_/python3-qllauncher',
      requires=['sleekxmpp', 'requests'],
      description='QuakeLive Library implements interaction between QuakeLive network and QuakeLive game client.'
      )