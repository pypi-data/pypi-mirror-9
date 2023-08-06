#!/usr/bin/env python
# -*- coding: utf-8 -*-

# if you are not using vagrant, just delete os.link directly,
# The hard link only saves a little disk space, so you should not care
import os
del os.link
 
from setuptools import setup, find_packages
 
VERSION = "0.1.1"
 
setup(
    # le nom de votre bibliothèque, tel qu'il apparaitre sur pypi
    name='sightcall_auth',
    version=VERSION,
 
    # Liste les packages à insérer dans la distribution
    # plutôt que de le faire à la main, on utilise la foncton
    # find_packages() de setuptools qui va cherche tous les packages
    # python recursivement dans le dossier courant.
    # C'est pour cette raison que l'on a tout mis dans un seul dossier:
    # on peut ainsi utiliser cette fonction facilement
    packages=find_packages(),
 
    # votre pti nom
    author="Raphaël Boucher",
 
    # Votre email, sachant qu'il sera publique visible, avec tous les risques
    # que ça implique.
    author_email="raphael.boucher@sightcall.com",
 
    # Une description courte
    description="Authenticate to the SightCall cloud",
 
    # Une description longue, sera affichée pour présenter la lib
    # Généralement on dump le README ici
    long_description=open('README.txt').read(),
 
    # dependencies
    install_requires = [ 'pyOpenSSL', 'requests' ],
 
    # Active la prise en compte du fichier MANIFEST.in
    include_package_data=True,
 
    # Une url qui pointe vers la page officielle de votre lib
    url='#TODO',
 
    # Il est d'usage de mettre quelques metadata à propos de sa lib
    # Pour que les robots puissent facilement la classer.
    # La liste des marqueurs autorisées est longue, alors je vous
    # l'ai mise sur 0bin: http://is.gd/AajTjj
    #
    # Il n'y a pas vraiment de règle pour le contenu. Chacun fait un peu
    # comme il le sent. Il y en a qui ne mettent rien.
    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 1 - Planning",
        "License :: OSI Approved",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.4",
        "Topic :: Communications",
    ],
 
 
    # C'est un système de plugin, mais on s'en sert presque exclusivement
    # Pour créer des commandes, comme "django-admin".
    # Par exemple, si on veut créer la fabuleuse commande "proclame-sm", on
    # va faire pointer ce nom vers la fonction proclamer(). La commande sera
    # créé automatiquement. 
    # La syntaxe est "nom-de-commande-a-creer = package.module:fonction".
    entry_points = {
        'console_scripts': [
            'extract_p12 = sightcall_auth.extract:extract',
        ],
    },
 
    # A fournir uniquement si votre licence n'est pas listée dans "classifiers"
    # ce qui est notre cas
    license="GPL",
 
)