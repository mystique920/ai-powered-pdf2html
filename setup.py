from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pdf2html-ai",
    version="0.1.1",
    author="Mystique",
    author_email="mystique@tuta.com",
    description="AI-powered PDF to HTML conversion using mistral-ocr and pixtral-12b",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/pdf2html_ai",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
    install_requires=[
        # List your dependencies here
        "mistralai",
        "python-dotenv",
        "requests",
        "PyPDF2",
        # Add other dependencies as needed
    ],
)
