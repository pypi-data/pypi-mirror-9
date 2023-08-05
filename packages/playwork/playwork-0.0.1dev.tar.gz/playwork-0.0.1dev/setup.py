from setuptools import setup, find_packages
version = '0.0.1'

setup(name='playwork',
      version=version,
      description="tornado, web framework, framework",

      long_description="""\
      a web framework based on the Tornado project
      """,

      classifiers=[
            "Development Status :: 1 - Planning",
            "Environment :: Web Environment",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: MIT License",
            "Natural Language :: English",
            "Operating System :: POSIX",
            "Programming Language :: Python :: 2.7",
            "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
      ], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='playwork, tornado, web, webframework, framework',
      author='younger shen',
      author_email='younger.x.shen@gmail.com',
      url='https://github.com/youngershen/playwork',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
        "tornado>=4.0.2"
      ],
      entry_points={'console_scripts': [
        'playwork-admin = playwork.command:command',
      ]},
      scripts=['playwork/bin/playwork-admin.py'],
      test_suite="playwork.test",
      tests_require=["pyflakes>=0.6.1", "pep8>=1.4.1"],
      )
