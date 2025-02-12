# NFC project

This is an NFC web application.

## Installation

You can download the repo or clone it using git clone.

```bash
git clone https://github.com/Abd-ElRahmanMamdouh/NFC_Project .
```

## Requirements
Create your venv and install the requirements

```bash
pip install -r requirements.txt
```

## Usage

Run migrate and create super user before using.
```bash
python manage.py migrate
python manage.py createsuperuser
```

## Features 
### Custom User Model
I used the Django's AbstractUser to extend the user model and updated it.
thats to add a role for the user (admin - regular) that we will use later.

### Login & Register Pages
### Profile Edit Pages
### Login With Token
auto created token when user login valid for 1 hour when expired the user forced to logout.


### Django Messages with sweet alert
you can go to templates/base/messages.html to edit colors and styling of sweet alert, see more on [Docs](https://sweetalert2.github.io/)

### Pagination ready template
at templates/base/pagination.html you can go to style your pagination nav, and if you have a model with pagination all you gotta do is include that template inside your list template like so, Note you set objects=page_obj if you using pagination in CVB and objects=your_list_varibale if you are using FBV
```html
CBV
{% include "base/pagination.html" with objects=page_obj %}
FBV
{% include "base/pagination.html" with objects=your_list_varibale %}
```
### Hide admin login page
Override the admin login page to show 404 page instead, remove that if you are not willing to have the custom login page

### Prevent superusers deletion
preventing superusers to be deleted by mistakes or by other superusers until the staff and superuser status removed.
also preventing deleting the first user (which should be the superuser created by createsuperuser command before lunching the project for other users)

## Useful Tips

I'm using flake8 and black to obtain clean code with Pep-8
create a file called .flake8
and paste these in it

```bash
[flake8]
exclude =
    migrations,
    __pycache__,
    manage.py,
    settings.py
max-line-length = 99
```

To see your mistakes run
```bash
flake8
```

You can go ahead and correct them manually or do it automatically with black like this

```bash
black path/to/file.py
```

# Happy Coding