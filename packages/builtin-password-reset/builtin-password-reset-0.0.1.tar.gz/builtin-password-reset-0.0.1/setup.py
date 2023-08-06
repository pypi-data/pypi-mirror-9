
# Use setuptools if we can
try:
    from setuptools.core import setup
except ImportError:
    from distutils.core import setup

setup(
    name='builtin-password-reset',
    version="0.0.1",
    description='',
    long_description='',
    author='Albert O\'Connor',
    author_email='info@albertoconnor.ca',
    url='http://albertoconnor.ca',
    download_url='',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Django",
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development",
    ],
    packages=[
        'builtin_password_reset',
    ],
)
