from setuptools import setup

setup(
    name='mallard',
    version='1.0.1',
    author='Nicolas Esteves',
    author_email='hamstahguru@gmail.com',
    packages=['mallard', 'mallard.examples'],
    url='https://github.com/hamstah/mallard',
    description='Library to send events to ducksboard.com',
    install_requires=[
        "requests>=2.4",
        "certifi>=14.05.14",
    ]
)
