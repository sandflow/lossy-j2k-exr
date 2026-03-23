#!/bin/bash

set -e

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <source_image> <is_linear_tf>"
    exit 1
fi

# first parameter

SRC="$1"
FN=$(basename "${SRC}")
ORIG_SIZE=$(stat -c%s -- "$SRC")

#second parameter

if [ -n "$2" ] && [ "$2" != "false" ] && [ "$2" != "0" ]; then
    LINEAR_TF=1
    MSE_ARG="--nlt asinh"
    echo "MSE: asinh"
else
    LINEAR_TF=0
    MSE_ARG="--nlt dwa"
    echo "MSE: dwa"
fi

# generate DWA results
DWA_Q="100"
DWA_FN="${FN%.exr}.dwa.${q}.exr"
./bin/exrmetrics ${SRC} -z dwab --convert -o ${DWA_FN} -l ${DWA_Q}
DWA_SIZE=$(stat -c%s -- "$DWA_FN")
DWA_MSE=$(./bin/exrmse ${SRC} ${DWA_FN} ${MSE_ARG})

echo "DWA"
echo "Q,MSE,size"
echo "${DWA_Q},${DWA_MSE},${DWA_SIZE}"

# generate OpenJPH results

TOLERANCE="0.01"
MIN="0.00001"
MAX="0.01"
MAX_ITER=100
ITER=0

if [ $LINEAR_TF -eq 1 ]; then
    OJPH_ARG=""
    echo "NLT + no transfer function"
else
    OJPH_ARG="-t"
    echo "No NLT + DWA transfer function"
fi

echo "OJPH"
echo "Q,MSE,size,diff"

while true; do
    HT_Q=$(echo "scale=6; ($MIN + $MAX) / 2" | bc)

    HT_FN="${FN%.exr}.ojph.${HT_Q}.exr"
    HTL_FN="${FN%.exr}.htl.${HT_Q}.exr"
    PIZ_FN="${FN%.exr}.ojph.${HT_Q}.piz.exr"
    ./bin/exrj2klossy_enc ${SRC} ${HT_FN} -q ${HT_Q} ${OJPH_ARG} > /dev/null
    HT_SIZE=$(stat -c%s -- "$HT_FN")
    ./bin/exrj2klossy_dec ${OJPH_ARG} ${HT_FN} ${HTL_FN} > /dev/null
    ./bin/exrmetrics ${HTL_FN} -z piz --convert -o ${PIZ_FN}
    rm ${HTL_FN}
    HT_MSE=$(./bin/exrmse ${MSE_ARG} ${SRC} ${PIZ_FN})

    DIFF=$(echo "scale=3; sqrt(($HT_SIZE - $DWA_SIZE)*($HT_SIZE - $DWA_SIZE))/$DWA_SIZE" | bc)

    echo "${HT_Q},${HT_MSE},${HT_SIZE},${DIFF}"

    if (( $(echo "$DIFF <= $TOLERANCE" | bc -l) )); then
        break
    fi

    rm ${HT_FN}
    rm ${PIZ_FN}

    if (( $(echo "$HT_SIZE > $DWA_SIZE" | bc -l) )); then
        MIN="$HT_Q"
    else
        MAX="$HT_Q"
    fi

    ITER=$((ITER + 1))

    if [ $ITER -gt $MAX_ITER ]; then
        echo "Error: Convergence not reached within $MAX_ITER iterations."
        return 1
    fi

done
