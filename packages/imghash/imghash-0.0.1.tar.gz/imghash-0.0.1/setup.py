from setuptools import setup


setup(
    name='imghash',
    version='0.0.1',
    description='',
    author='Florian Ludwig',
    author_email='f.ludwig@greyrook.com',
    packages=['imghash'],
    entry_points={
        'console_scripts': [
            'imghash = imghash:main',
            ],
    },
    install_requires=[
        'Pillow'
    ],
)