import numpy as np
import OpenImageIO as oiio
import argparse
import sys
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec


def read_exr(path):
    img = oiio.ImageInput.open(path)
    if not img:
        print(f"Error: Could not open {path}. {oiio.geterror()}")
        sys.exit(1)
    pixels = img.read_image("float")
    img.close()
    return pixels


def zoom_nearest(patch, factor):
    """Zoom a HxWxC patch by integer factor using nearest-neighbour."""
    h, w, c = patch.shape
    return patch.repeat(factor, axis=0).repeat(factor, axis=1)


def to_display(img):
    """Tone-map for display: clip to [0,1] after simple log normalisation."""
    img = np.clip(img, 0, None)
    img = img / (img.max() + 1e-10)
    return np.clip(img, 0, 1)


def main():
    parser = argparse.ArgumentParser(
        description="Find worst pixel between R and A, then show 64x64 patches from R, A, B.")
    parser.add_argument("R", help="Reference EXR image")
    parser.add_argument("A", help="Image A (compared against R to find worst pixel)")
    parser.add_argument("B", help="Image B")
    parser.add_argument("-o", "--output", default="worstpixel.png", help="Output plot path (default: worstpixel.png)")
    args = parser.parse_args()

    R = read_exr(args.R)
    A = read_exr(args.A)
    B = read_exr(args.B)

    if R.shape != A.shape or R.shape != B.shape:
        print(f"Error: image shapes differ: {R.shape}, {A.shape}, {B.shape}")
        sys.exit(1)

    height, width = R.shape[:2]

    # Relative difference between R and A, max across channels
    eps = 1e-6
    rel_diff = np.max(np.abs(R - A), axis=2)

    # Mask non-finite pixels
    finite = np.all(np.isfinite(R), axis=2) & np.all(np.isfinite(A), axis=2)
    rel_diff[~finite] = 0

    # Find the 16x16 block with the highest mean relative difference
    block = 16
    bh = height // block
    bw = width // block
    trimmed = rel_diff[:bh * block, :bw * block]
    block_means = trimmed.reshape(bh, block, bw, block).mean(axis=(1, 3))
    flat_idx = np.argmax(block_means)
    by, bx = np.unravel_index(flat_idx, block_means.shape)
    # Centre Z on the middle of the worst block
    zy = by * block + block // 2
    zx = bx * block + block // 2
    print(f"Worst 16×16 block top-left: ({bx * block}, {by * block}), mean relative difference: {block_means[by, bx]:.6f}")

    # Extract 64x64 patch centred at Z, clamped to image bounds
    half = 32
    y0 = max(0, zy - half)
    y1 = min(height, zy + half)
    x0 = max(0, zx - half)
    x1 = min(width, zx + half)

    patch_R = R[y0:y1, x0:x1]
    patch_A = A[y0:y1, x0:x1]
    patch_B = B[y0:y1, x0:x1]

    zoom = 8
    zoomed_R = zoom_nearest(patch_R, zoom)
    zoomed_A = zoom_nearest(patch_A, zoom)
    zoomed_B = zoom_nearest(patch_B, zoom)

    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    labels = [f"R  ({args.R})", f"A  ({args.A})", f"B  ({args.B})"]
    patches = [zoomed_R, zoomed_A, zoomed_B]

    for ax, patch, label in zip(axes, patches, labels):
        ax.imshow(to_display(patch), interpolation="nearest")
        ax.set_title(label, fontsize=9)
        ax.axis("off")

    fig.suptitle(
        f"64×64 patch centred on worst 16×16 block at Z=({zx},{zy}), zoomed 8×",
        fontsize=11)
    plt.tight_layout()
    plt.savefig(args.output, dpi=150)
    print(f"Saved plot to {args.output}")


if __name__ == "__main__":
    main()
