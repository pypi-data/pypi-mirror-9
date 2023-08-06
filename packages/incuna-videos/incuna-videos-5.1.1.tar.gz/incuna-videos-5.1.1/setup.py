from setuptools import setup, find_packages


setup(
    version='5.1.1',
    name='incuna-videos',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'FeinCMS>=1.10,<1.11',
        'django-imagekit>=3.2.1,<3.3',
    ],
    description='Generic extensible video content.',
    author='Incuna Ltd',
    author_email='admin@incuna.com',
    url='https://github.com/incuna/incuna-videos',
)
