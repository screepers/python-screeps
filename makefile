
SHELL:=/bin/bash
ROOT_DIR:=$(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))

.PHONY: all fresh dependencies install fulluninstall uninstall removedeps

all: dependencies

clean:
	rm -rf $(ROOT_DIR)/screepsapi/*.pyc
	# Remove existing environment
	if [ -d $(ROOT_DIR)/env ]; then \
		rm -rf $(ROOT_DIR)/env; \
	fi;
	if [ -d $(ROOT_DIR)/dist ]; then \
		rm -rf $(ROOT_DIR)/dist; \
	fi;
	if [ -d $(ROOT_DIR)/build ]; then \
		rm -rf $(ROOT_DIR)/build; \
	fi;
	if [ -d $(ROOT_DIR)/screepsapi.egg-info ]; then \
		rm -rf $(ROOT_DIR)/screepsapi.egg-info; \
	fi;

dependencies:
	if [ ! -d $(ROOT_DIR)/env ]; then python3 -m venv $(ROOT_DIR)/env; fi
	source $(ROOT_DIR)/env/bin/activate; yes w | python -m pip install -e .[dev]

package:
	source $(ROOT_DIR)/env/bin/activate; python setup.py bdist_wheel --universal
