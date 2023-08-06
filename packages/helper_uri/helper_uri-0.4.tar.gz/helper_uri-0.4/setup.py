try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='helper_uri',
    version='0.4',
    url='https://github.com/shuge/helper_uri',
    license='MIT License',
    author='Shuge Lee',
    author_email='shuge.lee@gmail.com',
    description='URI Helper',

    packages = [
        "helper_uri",
    ],
)
