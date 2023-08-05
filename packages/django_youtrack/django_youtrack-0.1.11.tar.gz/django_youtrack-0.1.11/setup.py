from distutils.core import setup

setup(
    name='django_youtrack',
    version='0.1.11',
    packages=['dj_youtrack', 'youtrack', 'httplib2'],
    py_modules=['urllib2_file'],
    url='https://github.com/ookami-kb/django_youtrack',
    license='',
    author='ookami-kb',
    author_email='ookami.kb@gmail.com',
    description='django_youtrack',
    requires=['django']
)
