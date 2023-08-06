from setuptools import setup, find_packages

version = '0.2.4'

setup(name='django-locations-base',
      version=version,
      description="A simple locations app for Django",
      long_description=open("README.md", "r").read(),
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          "Environment :: Web Environment",
          "Intended Audience :: End Users/Desktop",
          "Natural Language :: English",
          "Operating System :: OS Independent",
          "Framework :: Django",
          "Framework :: Django :: 1.7",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2",
          "Programming Language :: Python :: 3",
          "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: CGI Tools/Libraries",
          "Topic :: Utilities",
          "License :: OSI Approved :: MIT License",
          ],
      keywords='',
      author='Derek Stegelman',
      author_email='dstegelman@gmail.com',
      url='http://github.com/dstegelman/django-locations',
      license='MIT',
      packages=['locations',
                'locations.migrations'],
      include_package_data=True,
      zip_safe=False,
      install_requires=['django-localflavor>=1.1,<2.0', 'geopy>=1.9.1,<2.0']
    )
