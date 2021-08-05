.PHONY: all \
		setup \
		db \
		run \
		black \
		flake8 \
		mypy \
		coverage \

setup: venv/bin/activate ## project setup
	. venv/bin/activate; pip install -r requirements.txt
	
db: venv/bin/activate ## Run migrations
	. venv/bin/activate; python manage.py migrate
        
run: venv/bin/activate ## Run server
	. venv/bin/activate; python manage.py runserver
	
black: venv/bin/activate ## Run black
	. venv/bin/activate; black apps
	
flake8: venv/bin/activate ## Run flake8
	. venv/bin/activate; flake8 apps
	
mypy: venv/bin/activate ## Run mypy
	. venv/bin/activate; mypy apps

coverage: venv/bin/activate ## Run coverage
	. venv/bin/activate; coverage run --omit=*/venv/*,*/migrations/* manage.py test
