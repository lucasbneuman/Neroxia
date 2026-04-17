from setuptools import find_packages, setup

setup(
    name="whatsapp_bot_shared",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "langchain-core>=0.1.0",
    ],
)
