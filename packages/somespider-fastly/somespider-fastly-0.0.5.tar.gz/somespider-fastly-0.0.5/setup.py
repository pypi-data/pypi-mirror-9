from setuptools import setup

setup(
    name="somespider-fastly",
    version="0.0.5",
    author="Edwin Fuquen",
    author_email="tech@somespider.com",
    description="SomeSpider Fastly python API fork",
    keywords="fastly api somespider",
    url="https://github.com/somespider/fastly-py",
    packages=['fastly'],
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
