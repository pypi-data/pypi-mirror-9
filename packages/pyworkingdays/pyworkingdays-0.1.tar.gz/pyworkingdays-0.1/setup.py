from setuptools import setup, find_packages

setup(
    name = 'pyworkingdays',
    version = '0.1',
    packages = find_packages(),
    author = 'Augusto Destrero',
    author_email = 'a.destrero@gmail.com',
    description = 'Utility functions to deal with working days in date operations. With builtin localization support.',
    url = 'https://github.com/baxeico/pyworkingdays',
    download_url = 'https://github.com/baxeico/pyworkingdays/archive/0.1.tar.gz',
    install_requires = ['python-dateutil'],
    keywords = ['date', 'business', 'working']
)
