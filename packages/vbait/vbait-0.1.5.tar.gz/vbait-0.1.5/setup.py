from setuptools import find_packages, setup
#from distutils.core import setup

setup(
    author = 'Vitalii Baitaliuk',
    author_email = 'flampschelsea@gmail.com',
    name='vbait',
    version='0.1.5',
    #packages=['vbait','vbait.files_widget','vbait.thumbnails', 'vbait.vbplatform', 'vbait.vbplatform.errors'],
    packages = find_packages(),
    package_data={
        '': ['*.html', '*.css', '*.js', '*.json'],
        'vbait.files_widget': [
            'static/files_widget/css/*',
            'static/files_widget/img/*.jpg',
            'static/files_widget/img/*.gif',
            'static/files_widget/img/*.jpeg',
            'static/files_widget/img/*.png',
            'static/files_widget/img/file-icons/*',
            'static/files_widget/js/*',
            'templates/files_widget/*.html',
            'templates/files_widget/includes/*.html',
        ]},
    include_package_data = True,
    url="https://pypi.python.org/pypi/vbait/",
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    long_description=open('README.txt').read(),
)