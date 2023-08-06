from setuptools import setup, find_packages

setup(name='vidal-api.py',
      version='0.0.0',
      description="VIDAL REST API - SDK for api.vidal.fr",
      author='Software VIDAL',
      author_email='software@vidal.fr',
      url='https://github.com/softwarevidal/vidal-api.py',
      packages=['vidal'],
      install_requires=['requests', "feedparser"],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Apache Software License',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: Utilities'
      ]
)
