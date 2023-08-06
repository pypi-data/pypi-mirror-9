from setuptools import setup, find_packages

version = '0.3.3'

setup(name='django-downtime',
      version=version,
      description="Give your site a down page, or redirect to another error page.",
      long_description=open("README.md", "r").read(),
      classifiers=[
                   "Development Status :: 5 - Production/Stable",
                   "Environment :: Web Environment",
                   "Intended Audience :: End Users/Desktop",
                   "Natural Language :: English",
                   "Operating System :: OS Independent",
                   "Framework :: Django",
                   "Programming Language :: Python",
                   "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: CGI Tools/Libraries",
                   "Topic :: Utilities",
                   "License :: OSI Approved :: MIT License",
                   ],
      keywords='',
      author='Derek Stegelman',
      author_email='dstegelman@gmail.com',
      url='http://github.com/dstegelman/django-downtime',
      license='MIT',
      packages=find_packages(),
      install_requires = [],
      include_package_data=True,
      zip_safe=False,
      )
