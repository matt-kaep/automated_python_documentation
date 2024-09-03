from setuptools import setup, find_packages

setup(
    name="autocode",  # Name of your package
    version="0.1.0",  # Version of your package
    packages=find_packages(),  # Automatically find packages in the directory
    include_package_data=True, # Include additional files in the package
    install_requires=[        # Optional: Add dependencies here
        # "dependency1",
        # "dependency2",
    ],
    entry_points={
        'console_scripts': [
            'autocode=autocode.main:run',  # Command to run: autocode
        ],
    },
    author="Your Name",         # Your name
    author_email="your.email@example.com",  # Your email
    description="A package to automatically document code",  # Description
    #long_description=open('README.md').read(),  # Long description from README
    #long_description_content_type="text/markdown",  # Format of long description
    #url="https://your-repo-link",  # URL to your repository or project website
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # License type
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',  # Minimum Python version required
)
