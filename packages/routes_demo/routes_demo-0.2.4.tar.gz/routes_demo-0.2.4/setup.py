from setuptools import setup, find_packages

setup(
    name="routes_demo",
    version="0.2.4",
    packages=find_packages(),
    install_requires=["routes", "webob", "netaddr", "oslo.config", "babel"],
)
