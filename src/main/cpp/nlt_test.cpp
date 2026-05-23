#include <iostream>
#include <cmath>
#include <cstdlib>
#include <vector>

#include "nlt.h"

int main(int argc, char** argv) {
    float max_float_diff = 0;
    int max_int_diff = 0;

    for (int i = -32767; i <= 32767; ++i) {
        half half_val = int16_to_half((int16_t) i);
        int16_t int_val = half_to_int16(half_val);
        half rt_half_val = int16_to_half(int_val);
        int16_t rt_int_val = half_to_int16(rt_half_val);

        float float_diff = std::abs((float)half_val - (float)rt_half_val);
        if (float_diff > max_float_diff) {
            max_float_diff = float_diff;
        }

        int int_diff = std::abs(int_val - i);

        if (int_diff > max_int_diff) {
            max_int_diff = int_diff;
        }

        int rt_diff = std::abs(int_val - rt_int_val);

        // Allow a small difference due to floating point rounding
        if (rt_diff > 0) {
            std::cerr << "Round trip failed for " << i
                      << " -> " << (float)int_val
                      << " -> " << rt_half_val
                      << " (diff: " << rt_diff << ")" << std::endl;
            return 1;
        }
    }

    std::cout << "Max float difference in round trip: " << max_float_diff << std::endl;
    std::cout << "Max int difference in round trip: " << max_int_diff << std::endl;

    // Test specific values
    if (half_to_int16(0.0f) != 0) {
        std::cerr << "0.0f did not map to 0" << std::endl;
        return 1;
    }

    std::cout << "All tests passed." << std::endl;
    return 0;
}
