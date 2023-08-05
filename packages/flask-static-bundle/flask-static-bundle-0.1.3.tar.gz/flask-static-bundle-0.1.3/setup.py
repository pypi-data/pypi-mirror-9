# encoding: utf-8

from distutils.core import setup

setup(
    name='flask-static-bundle',
    version='0.1.3',
    packages=['flask_static_bundle'],
    install_requires=['Flask', 'static-bundle'],
    author='Rikanishu',
    author_email='rikanishu@gmail.com',
    license='MIT',
    description='Flask extension for static-bundle',
    url='http://github.com/Rikanishu/flask-static-bundle',
    download_url='https://github.com/Rikanishu/flask-static-bundle/archive/master.zip',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],
    )