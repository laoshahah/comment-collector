"""
安装配置
"""
from setuptools import setup, find_packages

setup(
    name="comment-collector",
    version="1.0.0",
    description="跨平台评论采集与客户信息提取工具",
    author="Your Name",
    author_email="your@email.com",
    python_requires=">=3.9",
    packages=find_packages(),
    install_requires=[
        "playwright>=1.40.0",
        "PyQt6>=6.6.0",
        "pandas>=2.1.0",
        "openpyxl>=3.1.0",
        "beautifulsoup4>=4.12.0",
        "lxml>=4.9.0",
    ],
    entry_points={
        "console_scripts": [
            "comment-collector=main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
