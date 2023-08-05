from pip.req import parse_requirements
from setuptools import setup, find_packages

from pip.req import parse_requirements
from helga_github_meta import __version__ as version

requirements = [
    str(req.req) for req in parse_requirements('requirements.txt')
]

setup(
    name='helga-github-meta',
    version=version,
    description=('Provide information for github related metadata'),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Topic :: Communications :: Chat :: Internet Relay Chat',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Communications :: Chat :: Internet Relay Chat'],
    keywords='irc bot github-meta urbandictionary urban dictionary ud',
    author='Jon Robison',
    author_email='narfman0@gmail.com',
    url='https://github.com/narfman0/helga-github-meta',
    license='LICENSE',
    packages=find_packages(),
    include_package_data=True,
    py_modules=['helga_github_meta.plugin'],
    zip_safe=True,
    install_requires=requirements,
    test_suite='',
    entry_points = dict(
        helga_plugins=[
            'github-meta = helga_github_meta.plugin:github_meta',
        ],
    ),
)
