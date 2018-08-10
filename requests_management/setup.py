from setuptools import setup, find_packages

setup(
    name='requests_management',
    version='0.0.1',
    packages=find_packages(),
    include_package_data=True,
    url='',
    license='',
    author='Mohamed Salah',
    author_email='googexel@gmail.com',
    zip_safe=False,
    install_requires=[
        'flask', 'pytest', 'click', 'werkzeug'
    ],
    description=''
)
