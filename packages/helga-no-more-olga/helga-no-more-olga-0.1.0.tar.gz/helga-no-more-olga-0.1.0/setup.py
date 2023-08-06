from setuptools import setup, find_packages

setup(
    name='helga-no-more-olga',
    version='0.1.0',
    description='A helga matcher that tells people to talk to helga instead of olga',
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
    keywords='helga olga',
    author="Shaun Duncan",
    author_email="shaun.duncan@gmail.com",
    url="https://github.com/shaunduncan/helga-no-more-olga",
    packages=find_packages(),
    py_modules=['helga_no_more_olga'],
    include_package_data=True,
    zip_safe=True,
    entry_points=dict(
        helga_plugins=[
            'no_more_olga = helga_no_more_olga:no_more_olga',
        ],
    ),
)
