from setuptools import setup
from dictmessages import __version__, __description__

_setup_requires = ['Django >= 1.4.2']
_long_description = open('README.rst').read().strip()

setup(
    name="django-dictmessages",
    version=__version__,
    author="Mike Hurt",
    author_email="mike@mhtechnical.net",
    description=__description__,
    long_description=_long_description,
    license="MIT",
    keywords="django messages dictionary template utility",
    url="https://bitbucket.org/mhurt/django-dictmessages",
    packages=[
        'dictmessages',
        ],
    include_package_data=True,
    zip_safe=True,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    install_requires=_setup_requires,
    setup_requires=_setup_requires,
)
