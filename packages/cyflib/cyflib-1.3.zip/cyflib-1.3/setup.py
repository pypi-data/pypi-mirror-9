from distutils.core import setup
import cyflib
long_desc = open("cyflib/long_desc.txt").read()
setup(
    name='cyflib',
    author='cyflib',
    author_email='admin@cyflib.cu.cc',
    version=cyflib.__version__,
    packages=['cyflib', 'cyflib/packages/ecdsa', 'cyflib/packages'],
    data_files=[('txt', ['cyflib/README.md', 'cyflib/LICENSE.md', 'cyflib/changes.txt', 'cyflib/long_desc.txt'])],
    url='http://cyflib.cu.cc',
    license='Creative Commons Attribution 4.0 International Public License',
    description='CyfLib Python Library',
    download_url='http://cyflib.cu.cc/download',
    long_description=long_desc
)
