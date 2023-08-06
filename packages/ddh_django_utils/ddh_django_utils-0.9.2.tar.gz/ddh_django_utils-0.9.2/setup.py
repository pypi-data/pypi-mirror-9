from setuptools import setup, find_packages


setup(name='ddh_django_utils',
      version = '0.9.2',
      description = 'Reusable Django app containing utilities for DDH projects',
      url = 'https://github.com/kcl-ddh/ddh_django_utils',
      author = 'Jamie Norrish',
      author_email = 'jamie@artefact.org.nz',
      packages = find_packages(),
      package_data = {
          'ddh_utils': ['templates/includes/*.html']
      },
      classifiers = [
          'Framework :: Django',
          'Intended Audience :: Developers',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Topic :: Utilities',
      ],
)
