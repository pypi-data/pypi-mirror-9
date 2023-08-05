django-thjodskra
================

django-thjodskra is a simple app for integrating the icelandic national registry into your project.
You still need to aquire the data files through the proper channel. This project only contains django models and functions for dealing with the archaic fileformat provided by the registry distributors.

###Installation:
pip install django-thjodskra

###Usage:
thjodskra.models.Person corresponds to rows in the national registry.

python manage.py import_entities
This should only be used for the initial import of registry data, i.e. when you have an empty DB and a big text file containing the complete registry.

python manage.py fetch_update
Fetches update file via FTP, this file can then be used with update_people

Requires django settings:

	THJODSKRA = {
		'host': [Address of your update provider],
		'username': [FTP Username],
		'password': [FTP Password],
		'file': [Path and name of update file to fetch]
	}

python manage.py update_entities [filename]  
Imports people that have not yet been added to local database and updates the info of those who have.

This can then be added to any script or cronjob as needed.
