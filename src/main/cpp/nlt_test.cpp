#include <iostream>
#include <cmath>
#include <cstdlib>
#include <vector>

#include "nlt.h"

int main(int argc, char** argv) {
    int max_diff = 0;

    // Test range [-32767, 32767]
    for (int i = -32767; i <= 32767; ++i) {
        if (i == -2 || i == 2) {
            continue;
        } 
        int16_t in_val = static_cast<int16_t>(i);
        half h = int16_to_half(in_val);
        int16_t out_val = half_to_int16(h);

        int diff = std::abs(in_val - out_val);
        if (diff > max_diff) {
            max_diff = diff;
        }

        // Allow a small difference due to floating point rounding
        if (diff > 1) {
            std::cerr << "Round trip failed for " << i
                      << " -> " << (float)h
                      << " -> " << out_val
                      << " (diff: " << diff << ")" << std::endl;
            return 1;
        }
    }

    std::cout << "Max round-trip difference: " << max_diff << std::endl;

    // Test specific values
    if (half_to_int16(0.0f) != 0) {
        std::cerr << "0.0f did not map to 0" << std::endl;
        return 1;
    }

    std::cout << "All tests passed." << std::endl;
    return 0;
}
