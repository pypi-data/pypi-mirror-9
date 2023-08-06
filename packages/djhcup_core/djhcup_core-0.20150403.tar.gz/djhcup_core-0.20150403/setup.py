from distutils.core import setup


setup(
    name='djhcup_core',
    version='0.20150403',
    description='A django-based interface for warehousing HCUP data',
    long_description=open('README.rst').read(),
    keywords='HCUP SAS healthcare analysis pandas',
    license='MIT',
    author='T.J. Biel',
    author_email='tbiel@med.umich.edu',
    packages=['djhcup_core'],
    provides=['djhcup_core'],
    classifiers=[
        'Framework :: Django',
        'License :: OSI Approved :: MIT License',
        'Topic :: Scientific/Engineering',
    ],
    package_data={'djhcup_core': [
                    'templates/*.*',
                    'static/*.*',
                    'static/css/*.*',
                    'static/fonts/*.*',
                    ]
                    },
    requires=[
        'django (>= 1.6)',
        'celery (>= 3.1.0)',
        'pandas (>= 0.11.0)',
        'pyhcup (>= 0.1.6)'
    ],
)