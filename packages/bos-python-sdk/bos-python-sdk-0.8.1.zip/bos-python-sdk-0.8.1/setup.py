from setuptools import setup, find_packages

setup(
    name='bos-python-sdk',
    version='0.8.1',
    keywords = ('bos', 'sdk'),
    description='BOS-Python-SDk',
    license='Free',
    author='boss-rd',
    author_email='boss-rd@baidu.com',
    url='http://bce.baidu.com/Product/BOS.html',
    platforms = 'any',
    packages = find_packages('bce-python-sdk-0.8.1'),
    package_dir = {'':'bce-python-sdk-0.8.1'}
)
