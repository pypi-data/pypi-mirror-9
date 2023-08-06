from distutils.core import setup

import cmsplugin_instagram

version = cmsplugin_instagram.__version__

setup(
    name = 'cmsplugin_instagram',
    packages = ['cmsplugin_instagram'],
    version = version,
    description = 'A djangocms plugin displaying images of an instagram account',
    author = 'Christoph Reimers',
    author_email = 'christoph@superservice-international.com',
    license='BSD License',
    url = 'https://github.com/creimers/cmsplugin_instagram',
    keywords = ['djangocms', 'django', 'instagram',], 
    install_requires = ['django-cms>=3.0',],
    classifiers = [
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
    ],
    include_package_data=True,
)
