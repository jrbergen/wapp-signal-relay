#!/usr/bin/env python

aiofiles==0.6.0
appdirs==1.4.4
certifi==2020.12.5
cffi==1.14.5
click==7.1.2
consonance==0.1.2
cryptography==3.4.6
dissononce==0.34.3
ecdsa==0.14.1
fastapi==0.58.1
h11==0.9.0
httpcore==0.12.3
httptools==0.1.1
httpx==0.16.1
idna==3.1
protobuf==3.15.6
pyasn1==0.4.8
pycparser==2.20
pydantic==1.8.1
pypng==0.0.20
PyQRCode==1.2.1
python-axolotl==0.2.2
python-axolotl-curve25519==0.4.1.post2
python-jose==3.2.0
rfc3986==1.4.0
rsa==4.7.2
signal-cli-rest-api==0.1.99
six==1.15.0
sniffio==1.2.0
starlette==0.13.4
transitions==0.8.7
typing-extensions==3.7.4.3
uvicorn==0.11.8
uvloop==0.15.2
websockets==8.1
yowsup==3.2.3


setup(
    name='wapp-signal-relay',
    version='0.0.1',
    url='https://github.com/jrbergen/wapp-signal-relay',
    license='GPL-3+',
    author='Joost Bergen',
    tests_require=[],
    install_requires=[],
    description='Whatsapp to Signal message relayer',
)