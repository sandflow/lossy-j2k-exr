#ifndef NLT_H
#define NLT_H

#include <half.h>
#include <math.h>

static float FACTOR = 32767.0f / (logf(65504.0f) / 2.2f + 1.0f);

inline half int16_to_half(int16_t f)
{
    float sign = f < 0 ? -1.0f : 1.0f;
    float val = ((float) abs(f)) / FACTOR;

    if (val <= 1.0f)
    {
        return sign * powf(val, 2.2f);
    }

    return sign * expf(2.2f * (val - 1.0f));
}

static int16_t half_to_int16(half h)
{
    float val = (float) h;
    float sign = val < 0.0f ? -1.0f : 1.0f;
    val = fabsf(val);

    if (val <= 1.0f)
    {
        return sign * roundf(powf(val, 1.0f / 2.2f) * FACTOR);
    }

    return sign * roundf((logf(val) / 2.2f + 1.0f) * FACTOR);
}

#endif // NLT_H