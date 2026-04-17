from setuptools import setup, find_packages

setup(
    name='whatsapp_bot_engine',
    version='0.1.0',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    install_requires=[
        'whatsapp_bot_shared',
        'whatsapp_bot_database',
        'langchain>=0.1.0',
        'langchain-openai>=0.0.5',
        'langchain-core>=0.1.0',
        'langchain-community>=0.0.10',
        'langchain-text-splitters>=0.0.1',
        'langgraph>=0.0.20',
        'openai>=1.0.0',
        'chromadb>=0.4.0',
        'pydantic>=2.0.0',
        'python-dotenv>=1.0.0',
        'requests>=2.31.0',
    ],
)
