from setuptools import setup, find_packages

setup(name='django-lumberjack',
      version='0.2.1',
      description='Simple logging. Stored in database, accessed in Django admin.',
      url='http://github.com/lander2k2/django-lumberjack',
      author='Richard Lander',
      author_email='lander2k2@gmail.com',
      license='MIT',
      packages=find_packages(),
      install_requires=['django>=1.7'],
      zip_safe=False)

