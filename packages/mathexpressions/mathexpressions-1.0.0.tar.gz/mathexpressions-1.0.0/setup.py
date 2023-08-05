__author__ = 'Noah Peeters'

from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='mathexpressions',
      version='1.0.0',
      description='Python library for parsing and solving math expressions. Example Usage: ' +
                  'https://github.com/NoahPeeters/pymathexpressions/blob/master/example.py ' +
                  'Documentation is coming soon.',
      classifiers=[
          'Development Status :: 4 - Beta',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python',
          'Topic :: Text Processing :: Linguistic',
          'Topic :: Scientific/Engineering :: Mathematics'
      ],
      url='https://github.com/NoahPeeters/pymathexpressions',
      author='Noah Peeters',
      author_email='noah.peeters@icloud.com',
      license='MIT',
      packages=['mathexpressions'],
      zip_safe=False)