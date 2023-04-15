from setuptools import setup, find_packages

setup(
    name="pico_w_thermostat",
    author="Ian Kline",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    package_data={"": ["*.json"]},
    include_package_data=True,
)
