#ifndef NLT_H
#define NLT_H

#include <half.h>
#include <math.h>

static float FACTOR = 32767.0f / (logf(65504.0f) / 2.2f + 1.0f);

inline float to_linear(float x)
{
    float sign = x < 0 ? -1.0f : 1.0f;
    float v = fabsf(x);
    if (v <= 1.0f)
    {
        return sign * powf(v, 2.2f);
    }
    return sign * expf(2.2f * (v - 1.0f));
}

inline float from_linear(float x)
{
    float sign = x < 0 ? -1.0f : 1.0f;
    float v = fabsf(x);
    if (v <= 1.0f)
    {
        return sign * powf(v, 1.0f / 2.2f);
    }
    return sign * (logf(v) / 2.2f + 1.0f);
}

inline half int16_to_half(int16_t f)
{
    return to_linear((float) f / FACTOR);
}

static int16_t half_to_int16(half h)
{
    return (int16_t) roundf(from_linear((float) h) * FACTOR);
}

#endif // NLT_H