from distutils.core import setup
setup(
  name = 'django_localizejs_seo',
  packages = ['django_localizejs_seo'], 
  version = '0.2',
  description = 'A Python Django prerender middleware for Localize JS',
  author = 'Yoland Yan',
  author_email = 'yoland68@gmail.com',
  url = 'https://github.com/yoland68/django_localizejs_seo', 
  download_url = 'https://github.com/yoland68/django_localizejs_seo/tarball/0.2', 
  keywords = ['django', 'seo', 'prerender'], 
  classifiers = [],
  install_requires=[
    'autopep8==1.1.1',
    'cffi==0.9.2',
    'cryptography==0.8.1',
    'enum34==1.0.4',
    'gnureadline==6.3.3',
    'ipdb==0.8',
    'ipython==3.0.0',
    'ndg-httpsclient==0.3.3',
    'pep8==1.6.2',
    'pyasn1==0.1.7',
    'pycparser==2.10',
    'pyOpenSSL==0.14',
    'requests==2.6.0',
    'six==1.9.0'
  ],
)