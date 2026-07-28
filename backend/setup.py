"""Setup configuration for MedSafeAI backend."""
from setuptools import setup

setup(
    name="medsafeai-backend",
    version="1.0.0",
    python_requires=">=3.11,<3.14",
    description="FastAPI backend for Medical Side Effect Checker",
    install_requires=[
        "fastapi==0.115.6",
        "uvicorn[standard]==0.32.1",
        "python-multipart==0.0.20",
        "pydantic==2.8.2",
        "pydantic-core==2.20.1",
        "typing-extensions==4.11.0",
        "annotated-types==0.7.0",
        "starlette==0.41.2",
    ],
)
