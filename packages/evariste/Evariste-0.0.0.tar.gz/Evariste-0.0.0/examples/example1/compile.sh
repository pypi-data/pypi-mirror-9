#!/bin/bash

cd $(dirname $0)
rm -fr html index.html
mkdir html

../../bin/evariste evariste.setup -v | tee /dev/stderr > index.html
