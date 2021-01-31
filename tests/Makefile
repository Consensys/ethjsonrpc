ROOT_DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
GETH := $(ROOT_DIR)/bin/geth.sh
SOURCES = $(wildcard *.sol)
BINS = $(SOURCES:.sol=.bin)

.PHONY: start
start:
	@sh $(GETH) start

%.bin: %.sol
	@solc --bin --output-dir ${ROOT_DIR} $<

compile: $(BINS)

.PHONY: test
test: start compile
	@pytest -v -s && sh $(GETH) stop || sh $(GETH) stop

.PHONY: clean
clean:
	@rm -f ${BINS} && sh $(GETH) clean
