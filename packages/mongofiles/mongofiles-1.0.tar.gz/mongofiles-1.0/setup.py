try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='mongofiles',
    version='1.0',
    url='https://github.com/shuge/mongofiles',
    license='MIT License',
    author='Shuge Lee',
    author_email='shuge.lee@gmail.com',
    description='mongofiles for Humans',
    scripts = [
        "mongofiles.py",
    ],
)
