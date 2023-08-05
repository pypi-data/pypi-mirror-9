from setuptools import setup, find_packages


with open('README.rst') as fp:
        long_description = fp.read()


setup(
    name='acme.dchat',
    version='0.1',
    namespace_packages=['acme'],
    packages=find_packages(),
    author="Tomohiro NAKAMURA",
    author_email="quickness.net@gmail.com",
    description="This software aim to provide a chatting tool with the NTT docomo API",
    long_description=long_description,
    license="Apache Software License",
    keywords="chat",
    url="https://github.com/jptomo/acme.dchat",
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.4',
    ],

)
