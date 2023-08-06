from setuptools import setup, find_packages

from cmsplugin_polls import __version__


CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Environment :: Web Environment',
    'Framework :: Django',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Topic :: Communications',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: Message Boards',
    'Topic :: Internet :: WWW/HTTP :: Site Management',
]

setup(
    name='cmsplugin-polls',
    version=__version__,
    description='Django CMS polls plugin',
    author='Anton Egorov',
    author_email='anton.egoroff@gmail.com',
    url='https://github.com/satyrius/cmsplugin-polls',
    license='MIT',
    long_description=open('README.rst').read(),
    classifiers=CLASSIFIERS,
    platforms=['OS Independent'],
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'django-cms',
    ],
    tests_require=['tox==1.8.1'],
    zip_safe=False,
)
