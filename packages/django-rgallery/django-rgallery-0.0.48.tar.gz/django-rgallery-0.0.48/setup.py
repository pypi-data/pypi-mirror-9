# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='django-rgallery',
    version='0.0.48',  # Changes in install_requires (+ BeautifulSoup)
                       # + commands mkthumb and mediasync from view
    author=u'Oscar M. Lage Guitian',
    author_email='r0sk10@gmail.com',
    #packages=['rgallery'],
    packages=find_packages(),
    include_package_data=True,
    package_data={'': ['rgallery/templates',
                       'rgallery/static',
                       'rgallery/fixtures'],
                  'rgallery-example': ['rgallery-example/*']},
    url='http://bitbucket.org/r0sk/django-rgallery',
    license='BSD licence, see LICENSE file',
    description='Yet another Django Gallery App',
    zip_safe=False,
    long_description=open('README.rst').read(),
    install_requires=[
        "Django < 1.5",
        "South == 0.7.5",
        "PIL == 1.1.7",
        "django-braces == 1.4.0",
        "sorl-thumbnail == 11.12",
        "django-compressor == 1.3",
        "dropbox == 1.5.1",
        "django-tagging == 0.3.4",
        "django-taggit == 0.12.2",
        "django-tinymce == 1.5.3",
        "django-filebrowser-no-grappelli == 3.5.7",
        "BeautifulSoup == 3.2.1",
        #"hachoir-metadata==1.3.3",
        #"hachoir-parser==1.3.4",
        # ffprobe
    ],
    keywords="django application gallery",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
