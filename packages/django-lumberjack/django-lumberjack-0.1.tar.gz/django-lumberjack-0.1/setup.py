from setuptools import setup

setup(name='django-lumberjack',
      version='0.1',
      description='Simple logging. Stored in database, accessed in Django admin.',
      url='http://github.com/lander2k2/django-lumberjack',
      author='Richard Lander',
      author_email='lander2k2@gmail.com',
      license='MIT',
      packages=['lumberjack'],
      install_requires=['django>=1.4,<1.8'],
      zip_safe=False)

