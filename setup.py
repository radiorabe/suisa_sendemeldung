from setuptools import setup


with open('requirements.txt') as f:
    requirements = f.read().splitlines()


setup(name='suisa_sendemeldung',
      description='ACRCloud client for SUISA reporting',
      url='http://github.com/radiorabe/suisa_reporting',
      author='RaBe IT-Reaktion',
      author_email='it@rabe.ch',
      license='MIT',
      install_requires=requirements,
      packages=['suisa_sendemeldung'],
      entry_points = {
          'console_scripts': ['suisa_sendemeldung=suisa_sendemeldung.suisa_sendemeldung:main'],
      },
      zip_safe=True)
