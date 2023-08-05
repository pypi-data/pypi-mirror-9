from setuptools import setup, find_packages


with open('README.rst') as fp:
    long_description = fp.read()


setup(
    name='acme.hello',
    version='0.1',
    namespace_packages=['acme'],
    packages=find_packages(),
    author='Tomohiro NAKAMURA',
    author_email='quickness.net@gmail.com',
    description='This is a test program for namespace_packages.',
    long_description=long_description,
    license='Apache Software License',
    keywords='sample',
    url='https://github.com/jptomo/acme.hello',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: Apache Software License',
    ],

)
