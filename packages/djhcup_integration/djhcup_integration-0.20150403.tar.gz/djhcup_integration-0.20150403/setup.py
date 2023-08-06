from distutils.core import setup


setup(
    name='djhcup_integration',
    version='0.20150403',
    description='Integration module for the Django-HCUP Hachoir (djhcup)',
    #long_description=open('README.rst').read(),
    license='MIT',
    author='T.J. Biel',
    author_email='tbiel@med.umich.edu',
    packages=['djhcup_integration'],
    provides=['djhcup_integration'],
    classifiers=[
        'Framework :: Django',
        'License :: OSI Approved :: MIT License',
        'Topic :: Scientific/Engineering',
    ],
    requires=[
        'djhcup_core (>= 0.20150403)',
    ],
    package_data={'djhcup_integration': [
                    'templates/*.*',
                    'utils/*.*',
                    ]
                    },
)
