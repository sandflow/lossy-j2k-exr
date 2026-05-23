#!/bin/bash

set -e

FN="SPARKS_ACES_07500.exr"

# generate HTL results

HT_Q="0.00005 0.0001 0.0002 0.0003 0.0004 0.0005 0.0006 0.0007 0.0008 0.0009 0.001"

echo "HT"
echo "Q, MSE, SIZE"

for q in $HT_Q; do
  HT_FN="${FN%.exr}.ht.${q}.exr"
  HT_DEC_FN="${FN%.exr}.ht.dec.${q}.exr"
  PIZ_FN="${FN%.exr}.ht.${q}.piz.exr"
  ./bin/exrj2klossy_enc ${FN} ${HT_FN} -q ${q} > /dev/null
  SIZE=$(stat -c%s -- "$HT_FN")
  ./bin/exrj2klossy_dec ${HT_FN} ${HT_DEC_FN} > /dev/null
  ./bin/exrmetrics ${HT_DEC_FN} -z piz --convert -o ${PIZ_FN}
  rm ${HT_DEC_FN}
  MSE=$(./bin/exrmse ${FN} ${PIZ_FN})
  echo "${q},${MSE},${SIZE}"
done

# ./bin/exrmetrics SPARKS_ACES_01000.exr -z dwab --convert -o SPARKS_ACES_01000.dwaa.exr
# ./bin/exrmse SPARKS_ACES_01000.exr SPARKS_ACES_01000.htl.exr
# ./bin/exrj2klossy_enc SPARKS_ACES_01000.exr SPARKS_ACES_01000.htl.exr -q 0.001