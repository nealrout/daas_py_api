# daas_py_api_asset
## Project

Refrence of DaaS Project - https://github.com/nealrout/daas_docs

## Description

This is an implementation of Django to expose endpoints for generic object.  We are purposely making the project more granular and not using some of the built-in features to communicate with the database.  Instead of a model, serializer,  and ModelViewSet we are managing stored procedures in the DBMS, which the code calls.  I am doing this as a challange and to create a sepration between application code and DBMS code.  The DB developers can have fine control over the actions coming into the DB through funcations & stored procedures.

This also gives the ability to make the api generic.  The only requirement is to set th DOMAIN environment variable (such as 'asset').  It will then fetch all configurations from the daas_py_config.settings.toml file.  This is 100% configuration controlled, and there is nothing making it unique to any one domain.  

__The Liquibase project containing DB objects:__  
https://github.com/nealrout/daas_db


## Table of Contents

- [Requirements](#requirements)
- [Install-Uninstall](#install-uninstall)
- [Usage](#usage)
- [Package](#package)
- [Features](#features)
- [Miscellaneous](#miscellaneous)
- [Contact](#contact)

## Requirements
__Set .env variables for configuration__    
You can do this either in the .env file, or by setting environment variables in the container.  

DOMAIN='\<DOMAIN\>'  
i.e. asset, facility, etc.

ENV_FOR_DYNACONF='\<environment\>'  
_i.e. development, integration, production_  

DYNACONF_SECRET_KEY='\<secret_key\>'

## Install-Uninstall
__Install:__  
python -m pip install daas_py_api

__Uninstall:__  
python -m pip uninstall daas_py_api

__Rebuild from source:__  
python -m pip install --no-binary :all: .

## Usage
__Set correct directory:__  
cd .\daas_py_apy\api\  

__Start Django api:__  
python manage.py runserver

## Package
python -m build daas_py_config

<!-- python setup.py sdist
python setup.py sdist bdist_wheel -->

## Features
- List all objects from database.
- Post to get objects by field.
- Upsert DB.
- Get and upsert SOLR.

## Miscellaneous

### To create new virtual environment  
python -m venv .venv

### To activate the virtual environment for this project
..\.venv\Scripts\activate

### Django (notes only)
__To create a new bootstrapped projects:__  
django-admin startproject api

cd api  

__To create a new application:__  
python manage.py startapp api

__To handle required migrations by built in tools:__  
python manage.py makemigrations  
python manage.py migrate

## Contact
Neal Routson  
nroutson@gmail.com