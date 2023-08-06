# Django Metrics

This is a very basic Django app that provides an interface to add metrics code snippets from the Django admin.

## Installation
* `pip install django_metrics`

## Usage

1. Add 'metrics' to the `INSTALLED_APPS` in your `settings.py` file.
2. Use the metrics template tags `{% metrics %}` to render the code snippets in a template, you need to load the tag using {% load metrics_tags %}.

## Requirements
This was only tested with Django 1.7 and Python 2.7

## License
WTFPL http://www.wtfpl.net/
