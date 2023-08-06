from distutils.core import setup


setup(
    name='djhcup_staging',
    version='0.20150403',
    description='Staging module for the Django-HCUP Hachoir (djhcup)',
    #long_description=open('README.rst').read(),
    license='MIT',
    author='T.J. Biel',
    author_email='tbiel@med.umich.edu',
    packages=['djhcup_staging'],
    provides=['djhcup_staging'],
    classifiers=[
        'Framework :: Django',
        'License :: OSI Approved :: MIT License',
        'Topic :: Scientific/Engineering',
    ],
    package_data={'djhcup_staging': [
                    'templates/*.*',
                    'utils/*.*',
                    'management/*.*',
                    'management/commands/*.*',
                    ]
                    },
    requires=[
        'djhcup_core (>= 0.20150403)',
    ],
)
