from setuptools import setup, find_packages

setup(
    name='django-waffle-session',
    version='0.1.7',
    description='A feature flipper for Django.',
    long_description=open('README.rst').read(),
    author='Francis Mwangi',
    author_email='francismwangi152@gmail.com',
    url='https://github.com/mwaaas/django-waffle-session',
    license='BSD',
    packages=find_packages(exclude=['test_app', 'test_settings']),
    include_package_data=True,
    package_data={'': ['README.rst']},
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
