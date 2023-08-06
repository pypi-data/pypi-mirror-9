from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()


setup(name='pytidyclub',
      version='0.0.7',
      description='A simple Python wrapper for the TidyClub API',
      long_description=readme(),
      classifiers=[
          'Development Status :: 2 - Pre-Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Natural Language :: English',
          'Programming Language :: Python',
          'Topic :: Internet',
          'Topic :: Internet :: WWW/HTTP',
      ],
      keywords=['tidyclub', 'club', 'society', 'api'],
      url='http://github.com/kyerussell/pytidyclub',
      author='Kye Russell',
      author_email='me@kye.id.au',
      license='MIT',
      packages=['pytidyclub'],
      install_requires=['requests'],
      test_suite='nose.collector',
      tests_require=['nose'],
      zip_safe=False)
