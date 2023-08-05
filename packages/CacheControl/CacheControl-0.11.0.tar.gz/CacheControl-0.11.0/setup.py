import setuptools

long_description = open('README.rst').read()

VERSION = '0.11.0'

setup_params = dict(
    name='CacheControl',
    version=VERSION,
    author='Eric Larson',
    author_email='eric@ionrock.org',
    license='MIT',
    url='https://github.com/ionrock/cachecontrol',
    keywords='requests http caching web',
    packages=setuptools.find_packages(),
    description='httplib2 caching for requests',
    long_description=long_description,
    install_requires=[
        'requests',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Internet :: WWW/HTTP',
    ],
)


if __name__ == '__main__':
    setuptools.setup(**setup_params)
