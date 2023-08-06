from setuptools import setup


setup(
    name='python-josso-auth',
    description='A JOSSO backend for python-social-auth',
    keywords='python-social-auth,sso,josso',
    version='0.1.1',
    packages=['josso'],
    package_dir={'josso': 'josso'},
    package_data={'josso': ['wsdl/*.xml']},
    install_requires=['suds-jurko', 'six'],
    url='https://github.com/consbio/python-josso-auth',
    license='BSD'
)