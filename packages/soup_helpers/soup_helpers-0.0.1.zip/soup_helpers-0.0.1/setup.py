from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='soup_helpers',
      version='0.0.1',
      description='A set simple of BeautifulSoup4 unit test helpers',
      long_description=readme(),
      url='https://bitbucket.org/bigmassa/soup_helpers',
      author='Stuart George',
      author_email='stuart.bigmassa@gmail.com',
      license='MIT',
      packages=['soup_helpers'],
      install_requires=[
        'beautifulsoup4',
      ],
      test_suite='nose.collector',
      tests_require=['nose'],
      include_package_data=True,
      zip_safe=False)
