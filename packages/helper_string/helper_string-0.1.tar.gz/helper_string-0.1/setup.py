try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='helper_string',
    version='0.1',
    url='https://github.com/shuge/helper_string',
    license='MIT License',
    author='Shuge Lee',
    author_email='shuge.lee@gmail.com',
    description='String Helper',

    scripts = [
        "helper_string.py",
    ],
)
