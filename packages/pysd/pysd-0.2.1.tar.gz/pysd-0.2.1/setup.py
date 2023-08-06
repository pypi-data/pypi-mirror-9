from distutils.core import setup

setup(
    name='pysd',
    version='0.2.1',
    author='James Houghton',
    author_email='james.p.houghton@gmail.com',
    packages=['pysd', 'pysd.translators', 'pysd.functions'],
    url='https://github.com/JamesPHoughton/pysd',
    download_url='https://github.com/JamesPHoughton/pysd/archive/v0.2.1.tar.gz',
    license='LICENSE.txt',
    description='System Dynamics Modeling in Python',
    long_description='see https://github.com/JamesPHoughton/pysd',
    keywords=['System Dynamics', 'XMILE', 'Vensim'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Scientific/Engineering :: Information Analysis',
    ],
)