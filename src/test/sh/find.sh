#!/bin/bash

set -e

SRC="${1:-build/SPARKS_ACES_07500.exr}"
FN=$(basename "${SRC}")
ORIG_SIZE=$(stat -c%s -- "$SRC")

# generate DWA results
DWA_Q="45"
DWA_FN="${FN%.exr}.dwa.${q}.exr"
./bin/exrmetrics ${SRC} -z dwab --convert -o ${DWA_FN} -l ${DWA_Q}
DWA_SIZE=$(stat -c%s -- "$DWA_FN")
DWA_MSE=$(./bin/exrmse ${SRC} ${DWA_FN} -n)

echo "DWA"
echo "${DWA_Q},${DWA_MSE},${DWA_SIZE}"

# generate KDU results

C_RATIO=$(echo "scale=6; $DWA_SIZE / $ORIG_SIZE" | bc)
KDU_FN="${FN%.exr}.kdu.${q}.exr"
./bin/exrj2klossy_enc ${SRC} ${KDU_FN} -r ${C_RATIO} -t > /dev/null
KDU_SIZE=$(stat -c%s -- "$KDU_FN")
KDU_MSE=$(./bin/exrmse ${SRC} ${HT_FN})

exit(0)

# generate OpenJPH results

TOLERANCE="0.01"
MIN="0.00001"
MAX="0.01"
MAX_ITER=100
ITER=0

while true; do
    HT_Q=$(echo "scale=6; ($MIN + $MAX) / 2" | bc)

    HT_FN="${FN%.exr}.ht.${HT_Q}.exr"
    PIZ_FN="${FN%.exr}.ht.${HT_Q}.piz.exr"
    ./bin/exrj2klossy_enc ${SRC} ${HT_FN} -q ${HT_Q} > /dev/null
    ./bin/exrmetrics ${HT_FN} -z piz --convert -o ${PIZ_FN}
    HT_SIZE=$(stat -c%s -- "$HT_FN")
    HT_MSE=$(./bin/exrmse ${SRC} ${HT_FN})

    DIFF=$(echo "scale=3; sqrt(($HT_SIZE - $DWA_SIZE)*($HT_SIZE - $DWA_SIZE))/$DWA_SIZE" | bc)

    echo "${HT_Q},${HT_MSE},${HT_SIZE}, ${DIFF}"

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

# ./bin/exrmetrics SPARKS_ACES_01000.exr -z dwab --convert -o SPARKS_ACES_01000.dwaa.exr
# ./bin/exrmse SPARKS_ACES_01000.exr SPARKS_ACES_01000.htl.exr
# ./bin/exrj2klossy_enc SPARKS_ACES_01000.exr SPARKS_ACES_01000.htl.exr -q 0.001