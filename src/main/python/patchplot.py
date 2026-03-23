import numpy as np
import OpenImageIO as oiio
import argparse
import sys
import matplotlib.pyplot as plt


LUM_WEIGHTS = np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)


def read_exr(path):
    img = oiio.ImageInput.open(path)
    if not img:
        print(f"Error: Could not open {path}. {oiio.geterror()}")
        sys.exit(1)
    pixels = img.read_image("float")
    img.close()
    return pixels


def to_display(img, scale):
    """Linear tone-map: multiply by scale so that ref pixel lands at 0.5."""
    return np.clip(img * scale, 0, 1)


def extract_patch(img, cx, cy, half=32):
    height, width = img.shape[:2]
    y0 = max(0, cy - half)
    y1 = min(height, cy + half)
    x0 = max(0, cx - half)
    x1 = min(width, cx + half)
    return img[y0:y1, x0:x1]


def zoom_nearest(patch, factor):
    return patch.repeat(factor, axis=0).repeat(factor, axis=1)


def main():
    parser = argparse.ArgumentParser(
        description="Show 64×64 patches from R, A, B centred at P, zoomed 8×.")
    parser.add_argument("R", help="Reference EXR image (shown in the middle)")
    parser.add_argument("A", help="Image A (shown on the left)")
    parser.add_argument("B", help="Image B (shown on the right)")
    parser.add_argument("P", help="Centre position as x,y (pixels from top-left)")
    parser.add_argument("-o", "--output", default="patchplot.png",
                        help="Output path (default: patchplot.png)")
    args = parser.parse_args()

    cx, cy = (int(v) for v in args.P.split(","))

    R = read_exr(args.R)
    A = read_exr(args.A)
    B = read_exr(args.B)

    if R.shape != A.shape or R.shape != B.shape:
        print(f"Error: image shapes differ: {R.shape}, {A.shape}, {B.shape}")
        sys.exit(1)

    # Tone-map scale: pixel at P in R should map to luminance 0.5
    ref_lum = float(np.dot(np.clip(R[cy, cx, :3], 0, None), LUM_WEIGHTS))
    if ref_lum <= 0:
        ref_lum = 1e-3
    scale = 0.5 / ref_lum
    print(f"Reference luminance at ({cx}, {cy}): {ref_lum:.6f}, scale: {scale:.4f}")

    # Extract, tone-map and zoom patches; order is A, R, B
    images = [A, R, B]
    titles = [f"A — {args.A}", f"R — {args.R}", f"B — {args.B}"]
    patches = [zoom_nearest(to_display(extract_patch(img, cx, cy, 16), scale)[:, :, :3], 8)
               for img in images]

    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    for ax, patch, title in zip(axes, patches, titles):
        ax.imshow(patch, interpolation="nearest")
        ax.set_title(title, fontsize=9)
        ax.axis("off")

    fig.suptitle(f"64×64 patch centred at ({cx}, {cy}), zoomed 8×", fontsize=11)
    plt.tight_layout()
    plt.savefig(args.output, dpi=150, bbox_inches="tight")
    print(f"Saved plot to {args.output}")


if __name__ == "__main__":
    main()
