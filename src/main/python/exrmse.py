import numpy as np
import OpenImageIO as oiio
import argparse
import sys


def read_exr(path):
    img = oiio.ImageInput.open(path)
    if not img:
        print(f"Error: Could not open {path}. {oiio.geterror()}")
        sys.exit(1)
    pixels = img.read_image("float")
    img.close()
    return pixels


def main():
    parser = argparse.ArgumentParser(description="Compute log MSE between two EXR images.")
    parser.add_argument("a", help="Reference EXR image")
    parser.add_argument("b", help="Distorted EXR image")
    args = parser.parse_args()

    a = read_exr(args.a)
    b = read_exr(args.b)

    if a.shape != b.shape:
        print(f"Error: image shapes differ: {a.shape} vs {b.shape}")
        sys.exit(1)

    # Mask out pixels where either image is non-finite
    finite = np.isfinite(a) & np.isfinite(b)

    a = a[finite].astype(np.float64)
    b = b[finite].astype(np.float64)

    log_a = np.log(np.maximum(a, 1e-10))
    log_b = np.log(np.maximum(b, 1e-10))

    mse = np.mean((log_a - log_b) ** 2)
    print(mse)


if __name__ == "__main__":
    main()
