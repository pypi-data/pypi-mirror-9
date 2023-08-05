from distutils.core import setup

version = '0.6.1'

setup(
  name = 'gini',
  packages = ['gini'], # this must be the same as the name above
  version = version,
  description = 'The un-intelligent Python AI library',
  long_description = '''Gini stands for "Gini is not intelligent." The library is for making tools that probably fall under the general field of AI, for people who don't care about AI.

Put another way, these are functions to help my scripts be polite, and act flexibly. I don't want my scripts to gain sentience. I just want them to interact with humans smoother.

''',
  author = 'Bill Gross',
  author_email = 'bill.gross@me.com',
  url = 'https://github.com/azraq27/gini',
  download_url = 'https://github.com/azraq27/gini/tarball/' + version,
  keywords = ['AI'],
  classifiers = [
      'Topic :: Scientific/Engineering',
      'Intended Audience :: Science/Research',
      'Development Status :: 3 - Alpha'
  ],
  install_requires=[
      'fuzzywuzzy',
      'python-Levenshtein'
  ]
)
