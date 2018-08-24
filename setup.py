from setuptools import setup, find_packages

setup(
    name='feature_request',
    version='0.0.2',
    packages=find_packages(),
    include_package_data=True,
    url='',
    license='',
    author='Mohamed Salah',
    author_email='googexel@gmail.com',
    zip_safe=False,
    install_requires=[
        'flask', 'flask-sqlalchemy', 'flask-marshmallow', 'marshmallow-sqlalchemy'
    ],
    extras_require={
        'test': [
            'pytest',
            'coverage',
            'dateparser'
        ],
    },
    test_suite='tests',
    description=''
)
