VENV := venv
PYTHON := ${VENV}/bin/python
PIP := ${VENV}/bin/pip


${VENV}/bin/activate:
	python3 -m venv ${VENV}

install: ${VENV}/bin/activate
	${PIP} install --upgrade pip
	${PIP} install dbt-duckdb

run:
	${VENV}/bin/dbt run

test:
	${VENV}/bin/dbt test

clean:
	rm -rf ${VENV} target logs dbt_packages *.duckdb
