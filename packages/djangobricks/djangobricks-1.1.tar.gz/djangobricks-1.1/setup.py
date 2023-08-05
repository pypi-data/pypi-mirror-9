import os
from distutils.core import setup

APP_NAME = 'djangobricks'
PACKAGES = ['%s.templatetags',]

root_dir = os.path.dirname(__file__)
if root_dir:
    os.chdir(root_dir)

data_files = []
for dirpath, dirnames, filenames in os.walk(APP_NAME):
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
    if '__init__.py' in filenames:
        continue
    elif filenames:
        for f in filenames:
            data_files.append(os.path.join(dirpath[len(APP_NAME)+1:], f))

packages = [APP_NAME] + [i % APP_NAME for i in PACKAGES]

setup(
    name=APP_NAME,
    version="%s.%s" % __import__(APP_NAME).VERSION[:2],
    packages=packages,
    package_data={APP_NAME: data_files},
    description = 'Heterogeneous models sorting',
    author = 'Germano Guerrini',
    author_email = 'germano.guerrini@gmail.com',
    url = 'https://github.com/GermanoGuerrini/django-bricks',
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
