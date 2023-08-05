from setuptools import setup, find_packages

APP_NAME = 'rohypnol'

setup(
    name=APP_NAME,
    version="%s.%s" % __import__(APP_NAME).VERSION[:2],
    packages=find_packages(),
    include_package_data=True,
    description = 'Simplified cache deletion',
    author = 'Germano Guerrini',
    author_email = 'germano.guerrini@gmail.com',
    url = 'https://github.com/GermanoGuerrini/django-rohypnol',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities',
    ],
)
