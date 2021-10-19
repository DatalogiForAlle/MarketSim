# Run development server
runserver:
	docker-compose up

check: flake8 test

# Execute tests within the docker image
test:
	docker-compose run --rm web django-admin compilemessages
	DJANGO_SETTINGS_MODULE=config.settings docker-compose run --rm web pytest 


# Check codestyle complies with PEP8
# black:
#	black --check -l 79 . --exclude=market/migrations --extend-exclude=accounts/migrations

flake8:
	flake8 --exclude market/migrations --extend-exclude accounts/migrations

# Reformat source files to adhere to PEP8 
tidy:
	black -79 . --exclude=market/migrations --extend-exclude=accounts/migrations

# Rebuild docker image
build:
	docker-compose build

# Open shell within running docker development container
shell:
	docker-compose exec web /bin/bash

production_stop:
	docker-compose -f docker-compose.prod.yml down --remove-orphans

production_start:
	docker-compose -f docker-compose.prod.yml up --build --remove-orphans -d

production_djangologs:
	docker logs markedsspilletdk_web_1

production_accesslogs:
	docker logs markedsspilletdk_nginx_1
