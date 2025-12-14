from setuptools import setup, find_packages

setup(
    name="podcast-generator",
    version="0.1.0",
    packages=find_packages(),
    py_modules=["run"],
    entry_points={
        'console_scripts': [
            'podcast=run:main',  # 创建 podcast 命令
            'pg-start=run:start_command',  # 创建 pg-start 命令
            'pg-stop=run:stop_command',    # 创建 pg-stop 命令
            'pg-restart=run:restart_command',
            'pg-status=run:status_command',
            'pg-logs=run:logs_command',
        ],
    },
    install_requires=[
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "pydantic>=1.8.0",
    ],
)