from distutils.core import setup

setup(name='NSLDS',
        version='1.5.2',
        description='Python wrapper to National Student Loan Data System',
        author='Derek Kaknes',
        author_email='derek.kaknes@gmail.com',
        url='TBD',
        py_modules=['nslds'],
        install_requires=['requests==2.5.3', 'lxml==3.4.0'],
        )
