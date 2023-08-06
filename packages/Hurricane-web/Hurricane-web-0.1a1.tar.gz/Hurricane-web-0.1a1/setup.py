from setuptools import setup, find_packages
import sys, os

version = '0.1a1'

setup(name='Hurricane-web',
      version=version,
      description="a simple web framework based on Tornado.",
      long_description="""\
      a simple web framework based on Tornado.
      """,
      classifiers=['Development Status :: 2 - Pre-Alpha',
                   'Environment :: Web Environment',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: MIT License',
                   'Natural Language :: English',
                   'Programming Language :: Python :: 2.7',
                   ],
      keywords='Hurricane, Tornado, web framework',
      author='younger shen',
      author_email='younger.x.shen@gmail.com',
      url='https://github.com/majia-tech/Hurricane',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          'tornado==4.1'
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
