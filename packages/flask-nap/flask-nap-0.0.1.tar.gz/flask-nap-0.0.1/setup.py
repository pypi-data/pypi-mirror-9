from setuptools import setup

setup(name='flask-nap',
      version="0.0.1",
      description='Flask REST Framework',
      url='https://github.com/aergener/nap',
      author='Adam Ergener',
      author_email='aergener@gmail.com',
      license='MIT',
      packages=['nap'],
      install_requires=['sqlalchemy>=0.9.7'],
      zip_safe=False,
)