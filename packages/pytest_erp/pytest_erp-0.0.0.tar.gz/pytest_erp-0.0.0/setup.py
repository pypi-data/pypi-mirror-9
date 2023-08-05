from setuptools import setup

setup(
    name="pytest_erp",
    description='py.test plugin to send test info to report portal dynamically',
    packages = ['pytest_plugin'],

    # the following makes a plugin available to pytest
    entry_points = {
        'pytest11': ['name_of_plugin = pytest_plugin.pytest_erp_plugin']
    },
    install_requires=[
        "requests >= 2.3.0"
    ],
)