#!/bin/bash

pyscript=$1
source venv/bin/activate
which python

if [ -n "$pyscript" ]; then
	python $pyscript
fi
ls
