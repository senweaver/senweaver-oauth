import os
import re
from setuptools import setup, find_packages

# Read version from __init__.py
with open(os.path.join('senweaver_oauth', '__init__.py'), 'r', encoding='utf-8') as f:
    version = re.search(r'__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read()).group(1)

# Read README.md for long description
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='senweaver-oauth',
    version=version,
    description='强大、灵活且易用的OAuth授权集成组件',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='senweaver',
    url='https://github.com/senweaver/senweaver-oauth',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    python_requires='>=3.8',
    keywords='oauth, wechat, weixin, 微信, senweaver',
    install_requires=[
        "requests>=2.28.0",
        "cryptography>=41.0.0",
        "cachetools>=5.0.0",
        "redis>=4.0.0"
    ],
    project_urls={
        'Bug Reports': 'https://github.com/senweaver/senweaver-oauth/issues',
        'Source': 'https://github.com/senweaver/senweaver-oauth',
    },
)