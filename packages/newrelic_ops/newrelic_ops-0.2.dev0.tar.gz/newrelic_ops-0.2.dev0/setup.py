from setuptools import setup

setup(name='newrelic_ops',
      version='0.2.dev',
      description='newrelic manipulation tool',
      long_description=open('README.md').read(),
      keywords='newrelic install saltstack automatic',
      url='https://github.com/Abukamel/newrelic_ops',
      author='Ahmed Kamel',
      author_email='k.tricky@gmail.com',
      license='MIT',
      packages=['newrelic_ops'],
      install_requires=['cement'],
      scripts=['bin/new_relic'],
      include_package_data=True,
      zip_safe=False)
