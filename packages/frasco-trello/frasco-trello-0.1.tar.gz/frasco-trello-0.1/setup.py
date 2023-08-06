from setuptools import setup, find_packages


setup(
    name='frasco-trello',
    version='0.1',
    url='http://github.com/frascoweb/frasco-trello',
    license='MIT',
    author='Maxime Bouroumeau-Fuseau',
    author_email='maxime.bouroumeau@gmail.com',
    description="Trello integration for Frasco",
    packages=find_packages(),
    zip_safe=False,
    platforms='any',
    install_requires=[
        'frasco-users',
        'py-trello==0.2.3-dev',
        'python-dateutil==2.4.0',
        'requests_oauthlib'
    ],
    dependency_links=[
        'git+https://github.com/sarumont/py-trello.git@84dcbefbd159abde52c57df8550237c0c21c5c71#egg=py-trello-0.2.3-dev'
    ]
)