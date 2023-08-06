#!/usr/bin/env python
from cloudwatchmon import VERSION
import os.path

from setuptools import find_packages, setup


def readme():
    path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(path):
        with open(path) as f:
            return f.read()


def stripped_reqs(fd):
    return (l.strip() for l in fd)


def parse_requirements(requirements):
    with open(requirements) as f:
        return [l for l in stripped_reqs(f) if l and not l.startswith("#")]


requirements_path = os.path.join(os.path.dirname(os.path.normpath(__file__)),
                                 'requirements.txt')


reqs = parse_requirements(requirements_path)


setup(name='cloudwatchmon',
      version=VERSION,
      description='Linux monitoring scripts for CloudWatch',
      long_description=readme(),
      url='https://github.com/osiegmar/cloudwatch-mon-scripts-python',
      author='Oliver Siegmar',
      author_email='oliver@siegmar.net',
      license='Apache License (2.0)',
      keywords="monitoring cloudwatch amazon web services aws ec2",
      zip_safe=True,
      packages=find_packages(),
      install_requires=reqs,
      entry_points={'console_scripts': [
          'mon-get-instance-stats.py=cloudwatchmon.cli.get_instance_stats:main',
          'mon-put-instance-stats.py=cloudwatchmon.cli.put_instance_stats:main',
          ]
      },
      classifiers=[
          'License :: OSI Approved :: Apache Software License',
          'Topic :: System :: Monitoring'
      ]
      )
