import os
from setuptools import setup, find_packages

# 读取README.md文件
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# 读取依赖项
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="senweaver-oauth",
    version="0.1.0",
    author="senweaver",
    description="强大、灵活且易用的OAuth授权集成组件",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/senweaver/senweaver-oauth",
    project_urls={
        "Bug Tracker": "https://github.com/senweaver/senweaver-oauth/issues",
        "Documentation": "https://www.senweaver.com/",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=requirements,
) 