# namespace
# install_requires
# test_requires
# nose_collector

# setup(
#   name='cocaine-cli',
#   version='0.1.0',
#   install_requires=[
#     'Click',
#   ],
#   entry_points='''
#     [console_scripts]
#     coke-db=cli:cli
#     cocaine-db=cli:cli
#     coke=webcli:cli
#     cocaine=webcli:cli
#   '''
# )


from setuptools import setup

setup(
    name="cocaine-cli",
    version="0.12.0-alpha14",
    author="Dmitry Unkovsky",
    author_email="oil.crayons@gmail.com",
    maintainer='Dmitry Unkovsky',
    maintainer_email='oil.crayons@gmail.com',
    url="https://github.com/cocaine/cocaine-pipeline",
    description="Cocaine Cloud Management Tool.",
    long_description="Cocaine cloud manager and cli",
    license="LGPLv3+",
    platforms=["Linux", "BSD", "MacOS"],
    namespace_packages=['cocaine'],
    include_package_data=True,
    zip_safe=False,
    packages=[
        "cocaine",
        "cocaine.cli"
    ],
    install_requires=open('./requirements.txt').read(),
    tests_require=open('./tests/requirements.txt').read(),
    test_suite='nose.collector',
    classifiers=[
        'Programming Language :: Python',
        # 'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        # 'Programming Language :: Python :: 3.2',
        # 'Programming Language :: Python :: 3.3',
        # 'Programming Language :: Python :: 3.4',
        "Programming Language :: Python :: Implementation :: CPython",
        # 'Development Status :: 1 - Planning',
        'Development Status :: 2 - Pre-Alpha',
        # 'Development Status :: 3 - Alpha',
        # 'Development Status :: 4 - Beta',
        # 'Development Status :: 5 - Production/Stable',
        # 'Development Status :: 6 - Mature',
        # 'Development Status :: 7 - Inactive',
    ],
    entry_points={
        'console_scripts': [
            "coke=cocaine.cli.webcli:cli",
            "cocaine=cocaine.cli.webcli:cli",
        ]
    }
)
