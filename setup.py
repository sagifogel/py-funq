from setuptools import setup

setup(
    version='0.0.1',
    name='py-funq',
    author='foldl',
    author_email='sagi.fogel@gmail.com',
    description='Funq dependency injection container port for python',
    extras_require={
        'tests': [
            'flake8~=6.0',
            'flake8-bugbear~=23.0',
            'flake8-isort~=6.0',
            'mypy~=0.991',
            'pytest~=7.0',
        ]
    }
)
