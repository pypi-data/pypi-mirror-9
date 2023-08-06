from setuptools import setup, find_packages

setup(
    name="routes_demo",
    version="0.2.9",
    packages=find_packages(),
    install_requires=["python-dev", "routes", "webob", "netaddr", "oslo.config", "babel", "iso8601", "eventlet", "oslo.db", "oslo.serialization"],
)
