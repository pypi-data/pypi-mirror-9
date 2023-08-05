import os
from setuptools import setup, find_packages
import uuid


requirements_path = os.path.join(
    os.path.dirname(__file__),
    'requirements.txt',
)
try:
    from pip.req import parse_requirements
    requirements = [
        str(req.req) for req in parse_requirements(
            requirements_path,
            session=uuid.uuid1()
        )
    ]
except ImportError:
    requirements = []
    with open(requirements_path, 'r') as in_:
        requirements = [
            req for req in in_.readlines()
            if not req.startswith('-')
            and not req.startswith('#')
        ]


setup(
    name='chrome-edit-server-gmail-filter',
    version='0.3.1',
    url='https://github.com/coddingtonbear/chrome-edit-server-gmail-filter',
    description=(
        'A chrome-edit-server plugin allowing one to edit Gmail messages'
    ),
    author='Tim Cuthbertson',
    author_email='tim@gfxmonk.net',
    classifiers=[
        'Operating System :: OS Independent',
    ],
    install_requires=requirements,
    include_package_data=True,
    packages=find_packages(),
    entry_points={
        'chrome_edit_server.plugins': [
            'gmail = chrome_edit_server_gmail_filter.filter:GmailFilter',
        ]
    },
)
