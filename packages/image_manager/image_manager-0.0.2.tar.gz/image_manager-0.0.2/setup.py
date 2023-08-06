
# Use setuptools if we can
try:
    from setuptools.core import setup
except ImportError:
    from distutils.core import setup

setup(
    name='image_manager',
    version="0.0.2",
    description='django-image-manager is a no none sense image hanlding system.',
    long_description='Allows the upload of files, creates thumbnails, and allow html level integeration.',
    author='Albert O\'Connor',
    author_email='info@albertoconnor.ca',
    url='https://bitbucket.org/albertoconnor/django-builtin-password-reset',
    download_url='',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Framework :: Django",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development"
    ],
    packages=[
        'image_manager'
    ],
)
