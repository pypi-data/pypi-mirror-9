try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='helper_datetime',
    version='0.5',
    url='https://github.com/shuge/helper_datetime',
    license='MIT License',
    author='Shuge Lee',
    author_email='shuge.lee@gmail.com',
    description='Date & Time Helper',

    packages = [
        "helper_datetime",
    ],
)
