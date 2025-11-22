from setuptools import find_packages, setup

setup(
    name="whatsapp_bot_database",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "sqlalchemy>=2.0.0",
    ],
)
