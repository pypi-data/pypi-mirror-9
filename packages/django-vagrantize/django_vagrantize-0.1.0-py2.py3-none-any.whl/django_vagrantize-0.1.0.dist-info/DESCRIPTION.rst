# Vagrantize

Vagrantize is a simple Django app that adds a shortcut `run` management 
command that will run the Django debug server on an externally visible 
port. It is just a shortcut for Django's builtin `runserver` command that 
is useful when doing development on a Django project using a Vagrant VM.
It is basically just shorthand for `python manage.py runserver 0.0.0.0:8000`.
## Installation

Install using pip:

```bash
pip install django-vagrantize
```

## Quick Start

1. Add "vagrantize" to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = (
    ...
    'vagrantize',
)
```

2. Run the Django server using the `run` command:

```bash
python manage.py run
```

Your application should be reachable at http://localhost:8000
*on the host machine*.

You may also specify an alternate port:

```bash
python manage.py run 8080
```



