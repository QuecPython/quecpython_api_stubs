from setuptools import setup


def readme():
    with open('README.rst', encoding='utf-8') as f:
        content = f.read()
    return content


def get_version():
    with open('VERSION', encoding='utf-8') as f:
        version = f.read()
    return version


setup(
    name='quecpython_stubs',
    version=get_version(),
    description='quecpython_stubs for IDE',
    long_description=readme(),
    long_description_content_type='text/x-rst',
    python_requires='>=3.7',
    license="MIT License",
    author='dustin.wei',
    author_email='dustin.wei@quectel.com',
    keywords=["QuecPython", "quecpython_stubs"],
    url='https://github.com/QuecPython/quecpython_api_stubs',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    platforms=["windows"],
    package_data={
        "quecpython_stubs": [
            '__init__.pyi',
            '__main__.py',
            'checkNet.pyi',
            'gc.pyi',
            'math.pyi',
            'sys.pyi',
            'ubinascii.pyi',
            'ucollection.pyi',
            'uio.pyi',
            'ujson.pyi',
            'uos.pyi',
            'urandom.pyi',
            'usocket.pyi',
            'ustruct.pyi',
            'utime.pyi'
        ]
    },
    packages=["quecpython_stubs"],
    install_requires=[
        'pywin32==306'
    ],
)
