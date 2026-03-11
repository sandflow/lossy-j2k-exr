#!/bin/bash

set -e

SRC="${1:-SPARKS_ACES_07500.exr}"
FN=$(basename "${SRC}")

run_dwa() {
  # generate DWA results
  DWA_Q="20 40 60 80 100 160"

  echo "DWA"
  echo "Q, MSE (dwa), MSE (arcsinh), SIZE"

  for q in $DWA_Q; do
    DWA_FN="${FN%.exr}.dwa.${q}.exr"
    ./bin/exrmetrics ${SRC} -z dwab --convert -o ${DWA_FN} -l ${q}
    SIZE=$(stat -c%s -- "$DWA_FN")
    MSE=$(./bin/exrmse -n ${SRC} ${DWA_FN})
    MSEA=$(./bin/exrmse -a ${SRC} ${DWA_FN})
    echo "${q},${MSE},${MSEA},${SIZE}"
  done
}
run_dwa

run_ojph() {
  # generate ojph results

  HT_Q="0.00005 0.0001 0.0002 0.0004 0.0008"

  echo "OJPH"
  echo "Q, MSE (dwa), MSE (arcsinh), SIZE"

  for q in $HT_Q; do
    HT_FN="${FN%.exr}.ht.${q}.exr"
    PIZ_FN="${FN%.exr}.ht.${q}.piz.exr"
    HTL_FN="${FN%.exr}.ht.${q}.htl.exr"
    ./bin/exrj2klossy_enc ${SRC} ${HT_FN} -q ${q} -t > /dev/null
    SIZE=$(stat -c%s -- "$HT_FN")
    ./bin/exrj2klossy_dec -t ${HT_FN} $HTL_FN > /dev/null
    ./bin/exrmetrics ${HTL_FN} -z piz --convert -o ${PIZ_FN}
    MSE=$(./bin/exrmse -n  ${SRC} ${PIZ_FN})
    MSEA=$(./bin/exrmse -a ${SRC} ${PIZ_FN})
    rm ${HT_FN}
    rm ${HTL_FN}
    echo "${q},${MSE},${MSEA},${SIZE}"
  done
}
run_ojph

run_ojph_linear() {
  # generate ojph results

  HT_Q="0.00005 0.0001 0.0002 0.0004 0.0008"

  echo "OJPH (linear)"
  echo "Q, MSE (dwa), MSE (arcsinh), SIZE"

  for q in $HT_Q; do
    HT_FN="${FN%.exr}.ht.${q}.exr"
    PIZ_FN="${FN%.exr}.ht.${q}.piz.exr"
    HTL_FN="${FN%.exr}.ht.${q}.htl.exr"
    ./bin/exrj2klossy_enc ${SRC} ${HT_FN} -q ${q} > /dev/null
    SIZE=$(stat -c%s -- "$HT_FN")
    ./bin/exrj2klossy_dec ${HT_FN} $HTL_FN > /dev/null
    ./bin/exrmetrics ${HTL_FN} -z piz --convert -o ${PIZ_FN}
    MSE=$(./bin/exrmse -n ${SRC} ${PIZ_FN})
    MSEA=$(./bin/exrmse -a ${SRC} ${PIZ_FN})
    rm ${HT_FN}
    rm ${HTL_FN}
    echo "${q},${MSE},${MSEA},${SIZE}"
  done
}
run_ojph_linear

run_kdu() {
  # generate KDU results

  HT_R="6 8 10 14 20"

  echo "KDU"
  echo "Q, MSE (dwa), MSE (arcsinh), SIZE"

  for r in $HT_R; do
    HT_FN="${FN%.exr}.kdu.${r}.exr"
    PIZ_FN="${FN%.exr}.kdu.${r}.piz.exr"
    HTL_FN="${FN%.exr}.kdu.${r}.htl.exr"
    ./bin/exrj2klossy_enc ${SRC} ${HT_FN} -r ${r} -t > /dev/null
    SIZE=$(stat -c%s -- "$HT_FN")
    ./bin/exrj2klossy_dec -t ${HT_FN} $HTL_FN > /dev/null
    ./bin/exrmetrics ${HTL_FN} -z piz --convert -o ${PIZ_FN}
    MSE=$(./bin/exrmse -n  ${SRC} ${PIZ_FN})
    MSEA=$(./bin/exrmse -a ${SRC} ${PIZ_FN})
    rm ${HT_FN}
    rm ${HTL_FN}
    echo "${r},${MSE},${MSEA},${SIZE}"
  done
}
run_kdu

run_kdu_linear() {
  # generate KDU results

  HT_R="6 8 10 14 20"

  echo "KDU linear"
  echo "Q, MSE (dwa), MSE (arcsinh), SIZE"

  for r in $HT_R; do
    HT_FN="${FN%.exr}.kdu.${r}.exr"
    PIZ_FN="${FN%.exr}.kdu.linear.${r}.piz.exr"
    HTL_FN="${FN%.exr}.kdu.${r}.htl.exr"
    ./bin/exrj2klossy_enc ${SRC} ${HT_FN} -r ${r} > /dev/null
    SIZE=$(stat -c%s -- "$HT_FN")
    ./bin/exrj2klossy_dec ${HT_FN} $HTL_FN > /dev/null
    ./bin/exrmetrics ${HTL_FN} -z piz --convert -o ${PIZ_FN}
    MSE=$(./bin/exrmse -n ${SRC} ${PIZ_FN})
    MSEA=$(./bin/exrmse -a ${SRC} ${PIZ_FN})
    rm ${HT_FN}
    rm ${HTL_FN}
    echo "${r},${MSE},${MSEA},${SIZE}"
  done
}
run_kdu_linear

# ./bin/exrmetrics SPARKS_ACES_01000.exr -z dwab --convert -o SPARKS_ACES_01000.dwaa.exr
# ./bin/exrmse SPARKS_ACES_01000.exr SPARKS_ACES_01000.htl.exr
# ./bin/exrj2klossy_enc SPARKS_ACES_01000.exr SPARKS_ACES_01000.htl.exr -q 0.001