from setuptools import setup
import glob

setup(
    name='brkt_sdk',
    version='0.1',
    description='Python SDK to the Bracket API',
    packages=[
        'brkt_requests'
    ],
    install_requires=['requests', 'oauthlib'],
    scripts=glob.glob('scripts/*')
)
