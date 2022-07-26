# Create a secure RESTful API using Django REST
*Jean-Corentin Loirat*
on 26/07/2022

Git hub link : https://github.com/BeanEden/Project_10.git

## Description :
"Softdest" is an API for an issue tracking system.


JSON documentation link : https://www.getpostman.com/collections/3933f9bf0f101d26f037

## Technologies :
* Django
* Python


## Set up :

### 1 - Download the zip file :
Install the elements in the repository of your choice

### 2 - Create a virtual environment in your repo and activate it :
* Terminal command : `cd path/to/selected/project/directory`
* Terminal command : `python -m venv env`
* Terminal command : `env/Scripts/activate.bat` (Windows)

### 3 - Import packages :
Import in your virtual environment the necessary packages
* Terminal command : `pip install -r requirements.txt`

### 4 - Check for migrations :
Check if the migrations are up to date
* Terminal command : `python manage.py makemigrations`
* Terminal command : `python manage.py migrate`

### 5 - Start the server :
Start the server in order to use the API
* Terminal command : `python manage.py runserver`


## Using the API
After starting the server, the user can start sending its requests to the API

### Connection :
* Create an user account
http://127.0.0.1:8000/signup/

* Start a user session
http://127.0.0.1:8000/login/

All other endpoints require to be authenticated

### Main endpoints : 
* Access your projects : 
http://127.0.0.1:8000/projects/
    * _(GET, POST)_

* Access a specific project : 
http://127.0.0.1:8000/projects/<int:project_id>/
    * _(GET, PUT, DELETE)_

* Access users of a specific project : http://127.0.0.1:8000/projects/<int:project_id>/users/
    * _(GET, POST)_

* Access a specific user assignment : 
http://127.0.0.1:8000/projects/<int:project_id>/issues/<int:issue_id>/
    * _(GET, PUT, DELETE)_

* Access issues of a specific project : http://127.0.0.1:8000/projects/<int:project_id>/issues/
    * _(GET, POST)_

* Access a specific issue : 
http://127.0.0.1:8000/projects/<int:project_id>/issues/<int:issue_id>/
    * _(GET, PUT, DELETE)_

* Access comments of a specific issue : 
http://127.0.0.1:8000/projects/<int:project_id>/issues/<int:issue_id>/comments/
    * _(GET, POST)_
  
* Access a specific comment : 
http://127.0.0.1:8000/projects/<int:project_id>/issues/<int:issue_id>/comments/<int:comment_id>/
    * _(GET, PUT, DELETE)_
  

### Access : 

Only the author of projects / issues / comments / user_assignments can update or delete their items.

The only exception is the author of the project.
He can also give permissions to modify while assigning people to a project.


### Security :

The API is secured against :
- authentication (access and refresh token, limited time session, only usewhile authenticated)
- injection (fields are slugs / alphanumeric / predetermined choices)

## API architecture : 
Models are managed in softdesk/models.py
5 models exists : 
* User
* Contributor (user_assignment project/user)
* Project
* Issues
* Comments

These Models are managed through the serializers in serializers.py

ViewSets are managed in views.py
ViewSets for login and authentication

## Database :
Database is in the file `db.sqlite3`.\

## Learn more :
Les fonctions et méthodes sont documentées via docstrings avec leurs utilisations, arguments et retours.
Classes and functions are documented with docstrings about their use, arguments and responses.