#
# This is a Unix Makefile for Lab 7
#

################################################################
# Installation targets
#
# Create the Python virtual environment
# The .PHONY: command makes this target always run when you type 'make venv',
# even if the 'venv' directory already exists.
#
.PHONY: venv
venv:
	make venv/pyvenv.cfg

venv/pyvenv.cfg:
	echo create the virtual environment and install the requirements
	python3 -m venv venv
	venv/bin/python3 -m pip install --upgrade pip
	venv/bin/python3 -m pip install -r requirements.txt

#
# Install the lab7.services file
.PHONY: install-lab7-service
install-lab7-service: venv/pyvenv.cfg
	sudo install lab7.service /etc/systemd/system/
	sudo systemctl daemon-reload
	sudo systemctl enable lab7
	sudo systemctl start lab7
	@# Do not overwrite lab7 as it may have been customized
	@if [ ! -r /etc/httpd/conf.d/lab7.conf ]; \
		then echo installing /etc/httpd/conf.d/lab7.conf ; \
		sudo install lab7.conf /etc/httpd/conf.d/ ; \
		else echo /etc/httpd/conf.d/lab7.conf already installed ; \
	fi
	@echo
	@echo Do not forget to edit ServerName in /etc/httpd/conf.d/lab7.conf, restart apache, and run certbot, and restart apache again
	@echo You may also need to restart your web browser.

################################################################
# Application targets
# Run the application locally for testing
# Note: your local machine must be authorized for your AWS account with the `aws` command.
local-app:
	venv/bin/flask --app app run --debug

# Print help for the application
help:
	venv/bin/flask --app app --help

# Create the s3 bucket and establish the CORS policy
.PHONY: init-s3
init-s3:
	venv/bin/flask --app app init-s3

.PHONY: init-db
init-db:
	make instance/server_db.sqlite

# Wipe the database and start over
.PHONY: wipe-db
wipe-db:
	/bin/rm -f instance/server_db.sqlite
	make init-db

# Create a new database
instance/server_db.sqlite:
	venv/bin/flask --app app init-db

# Generate a new api-key
.PHONY: new-apikey
new-apikey: instance/server_db.sqlite
	venv/bin/flask --app app new-apikey

# Dump the database
.PHONY: dump-db
dump-db: instance/server_db.sqlite
	venv/bin/flask --app app dump-db


#
# Software engineering targets

pylint:
	venv/bin/python3 -m pylint app
