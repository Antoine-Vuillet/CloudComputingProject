# CloudComputingProject

## Important files
main.py : Contains the core application logic and routes.
Dockerfile : Defines the environment for running the application in a Docker container.
requirements.txt : Specifies the Python dependencies for the project.

## Prerequisites
-Azure SQL Database: Ensure a database with a table Monsters containing monster data.
-Azure Active Directory: Credentials for accessing the database using a service principal.
-Python 3.8+: Ensure the correct Python version is installed.

## Features
Secure Azure SQL Database Integration:
    Utilizes MSAL for secure Azure Active Directory (AD) authentication.
    Retrieves data from the database using Azure AD tokens.

Web Interface:
    Serves HTML pages using Jinja2 templates.
    Includes a basic form for user interaction.

API Endpoints:
    GET /: Home page.
    GET /monsters: Lists all monsters from the database.
    GET /monsters/{name}: Retrieves detailed information about a specific monster.

## How to use
1. Ensure you have a database with a "Monsters" table that has at least a "name" column
2. Replace the following values with your own values:
tenant_id
client_id
client_secret
server_name
database_name


