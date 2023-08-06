#!/bin/bash
#
# Compile examples located in the /example directory (where / is the root of
# the repository).

ROOTDIR="$(dirname $0)/.."
EXAMPLEDIR=doc/examples
cd "$ROOTDIR/$EXAMPLEDIR"

for i in $(find -name '*.scl')
do
  basename=$(basename $i .scl)
  rm -f $basename.tex
  ../../bin/scal $i > $basename.tex
  xelatex $basename
done
