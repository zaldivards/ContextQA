from setuptools import setup, find_packages

install_requires: list[str] = []
long_description: str = ""

with open("requirements.txt", encoding="utf-8") as requirements_content:
    install_requires = requirements_content.readlines()

with open("../README.md", encoding="utf-8") as readme:
    long_description = readme.read()

setup(
    name="contextqa",
    version="{{VERSION_PLACEHOLDER}}",
    author="Christian Zaldivar",
    author_email="herrerachristian1897@gmail.com",
    maintainer="Christian Zaldivar",
    maintainer_email="herrerachristian1897@gmail.com",
    description="Chat with your data by leveraging the power of LLMs and vector databases",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    url="https://github.com/zaldivards/ContextQA/",
    keywords=["OpenAI", "LLM", "LLM client", "LLM app", "QA", "Agent", "LLM agent"],
    python_requires=">=3.11",
    packages=find_packages(),
    include_package_data=True,
    install_requires=install_requires,
    classifiers=[
        "Environment :: Console",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.11",
        "Framework :: FastAPI",
    ],
    entry_points={"console_scripts": ["contextqa = contextqa.cli:main"]},
)
