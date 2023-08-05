from distutils.core import setup
setup(
  name = 'django_opentok',
  packages = ['django_opentok'], # this must be the same as the name above
  version = '0.0.1',
  description = 'Integrate the opentok WebRTC into a Django project',
  author = 'Adam Wester',
  author_email = 'awwester@gmail.com',
  url = 'https://github.com/awwester/django-opentok', # use the URL to the github repo
  download_url = 'https://github.com/awwester/django-opentok/tarball/0.0.1', # I'll explain this in a second
  keywords = ['django', 'opentok', 'videochat'], # arbitrary keywords
  classifiers = [],
)