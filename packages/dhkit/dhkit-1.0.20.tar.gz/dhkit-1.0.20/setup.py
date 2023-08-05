import os
import io
import dhkit
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))


def read(*filenames, **kwargs):
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = []
    for filename in filenames:
        with io.open(filename, encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)

long_description = read('README')

setup(
    name='dhkit',
    version=dhkit.version,
    packages=['dhkit'],
    url='https://gitlab.com/smallpay/dhkit',
    license='',
    author='tufei',
    author_email='tufei@infohold.com.cn',
    description='smallpay python toolkit',
    long_description=long_description,
    install_requires=[],
    data_files=[],
)
