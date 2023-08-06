from setuptools import setup

setup(name='hyp-server',
    version='1.1.0',
    description='Hyperminimal https server',
    url='http://github.com/rnhmjoj/hyp',
    author='rnhmjoj',
    author_email='micheleguerinirocco@me.com',
    license='MIT-GPL',
    packages=['hyp'],
    entry_points={
        'console_scripts': ['hyp = hyp.hyp:main']
    },
    keywords=['http', 'https', 'ssl', 'tls', 'upload', 'server'],
    classifiers=[
        'Topic :: Internet :: WWW/HTTP :: HTTP Servers',
        'Topic :: Communications :: File Sharing',
        'Programming Language :: Python :: 3 :: Only',
        'License :: OSI Approved :: MIT License',
        'License :: OSI Approved :: GNU General Public License (GPL)',
    ])