from setuptools import setup, find_packages

requires = [
    'tornado>=4',
    'sockjs-tornado==1.0.1'
]

test_requires = [
    'mock',
    'nose',
    'coverage'
]

setup(
    name = 'sethpusher',
    install_requires = requires,
    tests_require=test_requires,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    test_suite = "nose.collector",
    version = '0.2.1',
    description = 'Tornado based pub/sub server powered by sockjs. Designed as a set of components.',
    author = 'jnosal',
    author_email = 'jacek.nosal@outlook.com',
    url = 'https://github.com/jnosal/seth-pusher',
    keywords = ['seth', 'tornado', 'push-server'],
    entry_points={
        'console_scripts': [
            'seth-pusher = sethpusher.default_server:main',
        ],
    },
    classifiers = [
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)