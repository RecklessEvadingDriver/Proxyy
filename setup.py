"""
Setup configuration for Proxyy
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="proxyy",
    version="1.0.0",
    author="RecklessEvadingDriver",
    description="A rotating proxy library with user-agent and IP rotation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/RecklessEvadingDriver/Proxyy",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.31.0",
    ],
    keywords="proxy, rotation, user-agent, ip-rotation, web-scraping, http-client",
)
