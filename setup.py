from setuptools import setup, find_packages
# Lire les dépendances depuis le fichier requirements.txt
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name="elevendoc",  # Nom de votre package
    version="1.1.3",  # Version de votre package
    packages=find_packages(),  # Trouver automatiquement les packages dans le répertoire
    include_package_data=True,  # Inclure des fichiers supplémentaires dans le package
    install_requires=requirements,  # Ajouter les dépendances ici
    entry_points={
        'console_scripts': [
            'elevendoc=elevendoc.main:run',  # Commande à exécuter : autocode
        ],
    },
    author="Matthieu Kaeppelin",  # Votre nom
    author_email="matthieu.kaeppelin@gmail.com",  # Votre email
    description="Un package pour documenter automatiquement le code",  # Description
    #long_description=open('README.md').read(),  # Longue description depuis README
    #long_description_content_type="text/markdown",  # Format de la longue description
    url="https://votre-lien-repo",  # URL vers votre dépôt ou site web du projet
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # Type de licence
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',  # Version minimale de Python requise
)