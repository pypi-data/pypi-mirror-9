from setuptools import setup, find_packages

# import os
# here = os.path.abspath(os.path.dirname(__file__))
# README = open(os.path.join(here, 'README.md')).read()

requires = [
    'u-msgpack-python',
    'tornado>4',
    'PyYaml',
    'jsonschema',
]

setup(
    name='pylogger',
    version='1.0',
    description='Send tailed logs to logstash with python',
    # long_description=README,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Logging',
    ],
    author='',
    author_email='',
    url='',
    keywords='logstash logger syslog tcp udp json',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=True,
    # test_suite='',
    # test_suite='nose.collector',
    install_requires=requires,
    # dependency_links=dependency_links,
    entry_points="""\
      [console_scripts]
      pylogger = pylogger.logger:main
      """,
)
