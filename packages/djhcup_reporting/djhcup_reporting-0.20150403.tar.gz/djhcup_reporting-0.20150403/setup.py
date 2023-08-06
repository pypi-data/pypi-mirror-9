from distutils.core import setup


setup(
    name='djhcup_reporting',
    version='0.20150403',
    description='Reporting module for the Django-HCUP Hachoir (djhcup)',
    license='MIT',
    author='T.J. Biel',
    author_email='tbiel@med.umich.edu',
    packages=['djhcup_reporting'],
    provides=['djhcup_reporting'],
    classifiers=[
        'Framework :: Django',
        'License :: OSI Approved :: MIT License',
        'Topic :: Scientific/Engineering',
    ],
    requires=[
        'djhcup_core (>= 0.20150403)',
    ],
    package_data={'djhcup_reporting': [
                    'management/commands/*.*',
                    'templates/*.*',
                    'templates/emails/*.*',
                    'utils/*.*',
                    'static/*.*',
                    'static/js/jqueryui/*.*',
                    'static/js/jqueryui/partials/*.*',
                    'static/js/jqueryui/external/jquery/*.*',
                    'static/js/jqueryui/images/*.*'
                    ]
                    },
)
