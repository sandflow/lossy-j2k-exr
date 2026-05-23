import numpy as np
import matplotlib.pyplot as plt

# All 65536 possible 16-bit patterns
bits = np.arange(65536, dtype=np.uint16)

# Interpret as float16
float_values = bits.view(np.float16).astype(np.float64)

# Interpret as signed int16
signed_values = bits.view(np.int16).astype(np.int32)

# Filter to positive finite values only
finite_mask = np.isfinite(float_values) & (float_values > 0)

fig, ax = plt.subplots(figsize=(12, 7))

x = float_values[finite_mask]

ax.plot(x, signed_values[finite_mask], linewidth=0.4, color='steelblue', label='int16 encoding')
ax.plot(x, 1600 *np.arcsinh(x / 0.0001), linewidth=1.0, color='orange', label='arcsinh(x / 0.00001)')
ax.legend()

ax.set_xlabel('Half-float value (float16 interpretation)')
ax.set_ylabel('Signed integer encoding (int16 interpretation)')
ax.set_title('All float16 values vs. their 16-bit signed integer encoding')
ax.set_xscale('log')
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('half_float_encoding.png', dpi=150)
plt.show()
print("Saved to half_float_encoding.png")
