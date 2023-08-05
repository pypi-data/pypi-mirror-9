from setuptools import setup

setup(name='DocDownloader',
      version='1.2.1',
      description='Downloads Documentation from ReadTheDocs in multiple formats',
      url='https://github.com/geekpradd/doc-downloader',
      author='Pradipta Bora',
      author_email='pradd@outlook.com',
      license='GNU GPL v2',
      packages=['DocDownloader'],
      install_requires=[
          'beautifulsoup4',
          'requests'  ,'wget' ],
      scripts=['bin/docdownloader'],
      classifiers=[
          "Development Status :: 4 - Beta",
          "Topic :: Utilities",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
          "Programming Language :: Python"
      ],
      zip_safe=False)
