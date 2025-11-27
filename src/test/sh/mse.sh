#!/bin/bash

set -e

FN="SPARKS_ACES_07500.exr"

# generate DWA results
DWA_Q="10 20 30 40 50 60 70 80 90 100"

echo "DWA"
echo "Q, MSE, SIZE"

for q in $DWA_Q; do
  DWA_FN="${FN%.exr}.dwa.${q}.exr"
  ./bin/exrmetrics ${FN} -z dwab --convert -o ${DWA_FN} -l ${q}
  SIZE=$(stat -c%s -- "$DWA_FN")
  MSE=$(./bin/exrmse ${FN} ${DWA_FN})
  echo "${q},${MSE},${SIZE}"
done

# generate HTL results

HT_Q="0.00005 0.0001 0.0002 0.0003 0.0004 0.0005 0.0006 0.0007 0.0008 0.0009 0.001"

echo "HT"
echo "Q, MSE, SIZE"

for q in $HT_Q; do
  HT_FN="${FN%.exr}.ht.${q}.exr"
  PIZ_FN="${FN%.exr}.ht.${q}.piz.exr"
  ./bin/exrj2klossy_enc ${FN} ${HT_FN} -q ${q} > /dev/null
  ./bin/exrmetrics ${HT_FN} -z piz --convert -o ${PIZ_FN}
  SIZE=$(stat -c%s -- "$HT_FN")
  MSE=$(./bin/exrmse ${FN} ${HT_FN})
  echo "${q},${MSE},${SIZE}"
done

# ./bin/exrmetrics SPARKS_ACES_01000.exr -z dwab --convert -o SPARKS_ACES_01000.dwaa.exr
# ./bin/exrmse SPARKS_ACES_01000.exr SPARKS_ACES_01000.htl.exr
# ./bin/exrj2klossy_enc SPARKS_ACES_01000.exr SPARKS_ACES_01000.htl.exr -q 0.001