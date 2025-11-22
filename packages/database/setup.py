"""Setup configuration for whatsapp_bot_database package."""

from setuptools import find_packages, setup

setup(
    name="whatsapp_bot_database",
    version="0.1.0",
    description="Shared database models and CRUD operations for WhatsApp Sales Bot",
    author="WhatsApp Sales Bot Team",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "sqlalchemy>=2.0.0",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
