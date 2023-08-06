from setuptools import setup, find_packages


setup(
    name='helga-reviewboard',
    version='0.2.0',
    description="A helga plugin for expanding shortcodes for code reviews on ReviewBoard",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Topic :: Communications :: Chat :: Internet Relay Chat',
        'Framework :: Twisted',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='helga reviewboard',
    author="Shaun Duncan",
    author_email="shaun.duncan@gmail.com",
    url="https://github.com/shaunduncan/helga-reviewboard",
    packages=find_packages(),
    py_modules=['helga_reviewboard'],
    include_package_data=True,
    zip_safe=True,
    entry_points=dict(
        helga_plugins=[
            'reviewboard = helga_reviewboard:reviewboard',
        ],
    ),
)
