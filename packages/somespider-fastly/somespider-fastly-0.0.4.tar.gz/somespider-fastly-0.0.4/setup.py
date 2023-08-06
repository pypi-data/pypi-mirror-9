from setuptools import setup

setup(
    name="somespider-fastly",
    version="0.0.4",
    author="Edwin Fuquen",
    author_email="tech@somespider.com",
    description="SomeSpider Fastly python API fork",
    keywords="fastly api somespider",
    url="https://github.com/somespider/fastly-py",
    packages=['fastly'],
    long_description=open('README.md').read(),
    classifiers=[
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "License :: OSI Approved :: MIT License",
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities"
    ],
    scripts=[
        "bin/purge_service",
        "bin/purge_key",
        "bin/purge_url"
    ]
)
