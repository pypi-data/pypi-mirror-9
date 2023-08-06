from setuptools import setup, find_packages

setup(
      name = 'hedgeye_analysis',
      version = '0.1.9',
      description = 'Python analysis tools used by Hedgeye',
      url = 'https://github.com/hedgeyedev/hedgeye-python-analysis/hedgeye_analysis',
      author='James Lavin',
      author_email='jlavin@hedgeye.com',
      license='MIT',
      packages=find_packages(exclude=['test','test.*']),
      install_requires=[
          'IPython',
          'matplotlib',
          'numpy',
          'pandas',
          'seaborn',
      ],
      test_suite='nose.collector',
      classifiers = [
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.4'
      ],
      zip_safe=False
      )
