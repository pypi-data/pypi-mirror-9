#!/usr/bin/env python

# Copyright 2012, refnode <refnode@gmail.com>
# All Rights Reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

.PHONY: python-buildout

RM = rm -rf
CP = cp

PROJECT_DIR := $(shell pwd)
SRC_ARCHIVE := $(shell python setup.py --fullname).tar.gz

LSB_VENDOR  := $(shell lsb_release -is | tr A-Z a-z)
LSB_RELEASE := $(shell lsb_release -sr)
LSB_ARCH    := $(shell uname -m)

BUILD_DIR_ROOT = $(HOME)/rpmbuild
BUILD_DIR_BUILD = $(BUILD_DIR_ROOT)/BUILD
BUILD_DIR_RPMS = $(BUILD_DIR_ROOT)/RPMS
BUILD_DIR_SOURCES = $(BUILD_DIR_ROOT)/SOURCES
BUILD_DIR_SPECS = $(BUILD_DIR_ROOT)/SPECS
BUILD_DIR_SRPMS = $(BUILD_DIR_ROOT)/SRPMS
BUILD_DIR_RESULT= $(BUILD_DIR_ROOT)/RESULT

RHEL_SPEC_FILE := $(shell ls pkg/rhel/*.spec)
RHEL_SRPM_FILE := $(shell rpmspec --query --srpm --queryformat="%{name}-%{version}-%{release}" $(RHEL_SPEC_FILE)).src.rpm
RHEL_MOCK_CONFIG ?= "$(LSB_VENDOR)-$(LSB_RELEASE)-$(LSB_ARCH)" 
RHEL_MOCK = sudo mock -r $(RHEL_MOCK_CONFIG) --resultdir=$(BUILD_DIR_RESULT)


python-buildout:
	/usr/bin/env python bootstrap.py
	bin/buildout

python-clean:
	@find . \( \
		-iname "*.pyc" \
		-or -iname "*.pyo" \
		\) -delete

python-release:	distclean
	python setup.py sdist

distclean: python-clean
	@$(RM) \
		bin/ \
		build/ \
		develop-eggs/ \
		dist/ \
		eggs/ \
		parts/ \
		*.egg-info/ \
		MANIFEST \
		.installed.cfg \
		RPM_BUILD_RESULT

# Red Hat Enterprise Family specific targets
# Shoud work for RHEL, CentOS and Fedora
# Default settings for Fedora
rhel-mock-init:
	$(RHEL_MOCK) --init

rhel-mock-clean:
	$(RHEL_MOCK) --clean

rhel-mock-shell:
	$(RHEL_MOCK) --no-clean --no-cleanup-after shell

rhel-rpmbuild-init: rhel-mock-init
	rpmdev-setuptree
	rpmdev-wipetree
	mkdir -p $(BUILD_DIR_RESULT)

rhel-release-srpm: python-release rhel-rpmbuild-init
	$(CP) $(PROJECT_DIR)/$(RHEL_SPEC_FILE) $(BUILD_DIR_SPECS)
	$(CP) $(PROJECT_DIR)/dist/$(SRC_ARCHIVE) $(BUILD_DIR_SOURCES)
	$(RHEL_MOCK) --no-cleanup-after --sources=$(BUILD_DIR_SOURCES) --buildsrpm --spec=$(BUILD_DIR_SPECS)/$(shell basename $(RHEL_SPEC_FILE))
	$(CP) $(BUILD_DIR_RESULT)/$(RHEL_SRPM_FILE) $(BUILD_DIR_SRPMS)

rhel-release-rpm: rhel-release-srpm 
	$(RHEL_MOCK) --no-clean --no-cleanup-after --rebuild $(BUILD_DIR_SRPMS)/$(RHEL_SRPM_FILE)
