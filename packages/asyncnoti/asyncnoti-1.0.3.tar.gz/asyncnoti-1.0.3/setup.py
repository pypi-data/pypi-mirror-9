from distutils.core import setup

setup(
    name='asyncnoti',
    packages=['asyncnoti'],
    version='1.0.3',
    description='Library to interact with the Asyncnoti API',
    url='https://github.com/asyncnoti/asyncnoti-python',
    download_url = 'https://github.com/asyncnoti/asyncnoti-python/tarball/1.0.3',
    author='Asyncnoti',
    author_email='admin@asyncnoti.com',
    keywords=['asyncnoti', 'websockets', 'realtime'],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP",
    ],
    license='MIT',
    install_requires=['six'],
    tests_require=['nose', 'mock'],
    test_suite='asyncnoti_tests',
)