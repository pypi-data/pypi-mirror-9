from distutils.core import setup
# import ipdb; ipdb.set_trace()
setup(
  name = 'django_localizejs_seo',
  packages = ['django_localizejs_seo'], 
  version = '0.1',
  description = 'A Python Django prerender middleware for Localize JS',
  author = 'Yoland Yan',
  author_email = 'yoland68@gmail.com',
  url = 'https://github.com/yoland68/django_localizejs_seo', 
  download_url = 'https://github.com/yoland68/django_localizejs_seo/tarball/0.1', 
  keywords = ['django', 'seo', 'prerender'], 
  classifiers = [],
  install_requires=[
        "requests",
  ],
)