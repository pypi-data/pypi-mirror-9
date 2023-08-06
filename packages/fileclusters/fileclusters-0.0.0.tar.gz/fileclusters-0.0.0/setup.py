from setuptools import setup, find_packages

version = "0.0.0"

long_description=""
try:
    long_description="COMODA Fileclusters"
except Exception:
    pass

license=""
try:
    license='MIT_License.txt'
except Exception:
    pass


setup(
    name='fileclusters',
    description='COMODA Fileclusters',
    author='Pablo Saavedra',
    author_email='pablo.saavedra@interoud.com',
    version=version,
    # url='',
    packages=find_packages(),
    package_data = {
    },

    include_package_data=True,
    scripts=[
    ],
    zip_safe=False,
    install_requires=[
        "setuptools",
        "django >=1.6, <1.7",
        "python-dateutil",
        "httplib2",
        "simplejson",
        "slugify",
        "django-dajax",
        "django-dajaxice",
        "django-sekizai ",
        "paramiko ",
        "chardet ",
        "Pillow ",
        "pytz ",
        "django-guardian",
        "easy-thumbnails",
        "South",
        "django-userena",
        "DateUtils",
        "pyncomings",
        "psycopg2",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: Django",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Multimedia :: Video",
    ],
    long_description=long_description,
    license=license,
    keywords = "fileclusters",

    data_files=[
    ],



)
