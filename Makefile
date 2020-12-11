SUBDIRS := $(wildcard */.)

.PHONY: default test clean
default: check

.PHONY: all
all: $(SUBDIRS)

.PHONY: $(SUBDIRS)
$(SUBDIRS):
	$(MAKE) -C $@

# Installs pre-commit hooks
.PHONY: install-hooks
install-hooks:
	pre-commit install -f --install-hooks

# Checks files for encryption
.PHONY: check
check:
	pre-commit run --all-files
