import numpy as np
import OpenImageIO as oiio
import argparse
import sys
import matplotlib.pyplot as plt



def read_exr(path):
    img = oiio.ImageInput.open(path)
    if not img:
        print(f"Error: Could not open {path}. {oiio.geterror()}")
        sys.exit(1)
    pixels = img.read_image("float")
    img.close()
    return pixels


LUM_WEIGHTS = np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)


def to_display(img, ref_lum):
    """Linear tone-map img so that [ref_lum/16, ref_lum*16] maps to [0, 1]."""
    lo = ref_lum / 1.7
    hi = ref_lum * 1.7
    return np.clip((img - lo) / (hi - lo), 0, 1)


def main():
    parser = argparse.ArgumentParser(
        description="Plot a disc with three image slices centred at a given position.")
    parser.add_argument("R", help="Reference EXR image")
    parser.add_argument("A", help="Image A")
    parser.add_argument("B", help="Image B")
    parser.add_argument("P", help="Centre position as x,y (pixels from top-left)")
    parser.add_argument("--radius", type=int, default=64, help="Disc radius in pixels (default: 64)")
    parser.add_argument("-o", "--output", default="discplot.png", help="Output path (default: discplot.png)")
    args = parser.parse_args()

    cx, cy = (int(v) for v in args.P.split(","))
    radius = args.radius

    R = read_exr(args.R)
    A = read_exr(args.A)
    B = read_exr(args.B)

    if R.shape != A.shape or R.shape != B.shape:
        print(f"Error: image shapes differ: {R.shape}, {A.shape}, {B.shape}")
        sys.exit(1)

    height, width = R.shape[:2]

    # Luminance of R at P, used as tone-map anchor
    ref_lum = float(np.dot(np.clip(R[cy, cx, :3], 0, None), LUM_WEIGHTS))
    if ref_lum <= 0:
        ref_lum = 1e-3
    print(f"Reference luminance at ({cx}, {cy}): {ref_lum:.6f}")

    # Build canvas: square bounding box around the disc
    size = radius * 2 + 1
    canvas = np.zeros((size, size, 4), dtype=np.float32)  # RGBA

    # Pixel offsets relative to centre
    ys, xs = np.mgrid[-radius:radius + 1, -radius:radius + 1]
    dist = np.sqrt(xs ** 2 + ys ** 2)
    inside = dist <= radius

    # Angle for each pixel: 0 at right, increasing counter-clockwise
    angle = np.arctan2(-ys, xs) % (2 * np.pi)  # negate ys so 0° is at top-right

    # Three equal sectors of 120° each
    sector = (angle / (2 * np.pi / 3)).astype(int) % 3  # 0 = R, 1 = A, 2 = B
    sources = [to_display(R, ref_lum), to_display(A, ref_lum), to_display(B, ref_lum)]

    for s, src in enumerate(sources):
        mask = inside & (sector == s)
        # Image coordinates
        img_y = cy + ys[mask]
        img_x = cx + xs[mask]

        # Clamp to image bounds
        valid = (img_y >= 0) & (img_y < height) & (img_x >= 0) & (img_x < width)
        py = np.where(valid, img_y, 0)
        px = np.where(valid, img_x, 0)

        rgb = src[py, px, :3]
        rgb[~valid] = 0.0

        canvas_y = ys[mask] + radius
        canvas_x = xs[mask] + radius
        canvas[canvas_y, canvas_x, :3] = rgb
        canvas[canvas_y, canvas_x, 3] = np.where(valid, 1.0, 0.5)

    # Draw sector dividing lines
    line_angles = [0, 2 * np.pi / 3, 4 * np.pi / 3]
    for la in line_angles:
        for r in range(radius + 1):
            lx = int(round(r * np.cos(la)))
            ly = int(round(-r * np.sin(la)))
            canvas[ly + radius, lx + radius] = [0, 0, 0, 1]

    # Zoom 4x with nearest-neighbour
    zoomed = canvas.repeat(4, axis=0).repeat(4, axis=1)

    # Plot
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.imshow(zoomed, interpolation="nearest", origin="upper")
    ax.axis("off")

    # Sector labels placed just outside the disc at each sector's midpoint angle
    sector_labels = [f"R\n{args.R}", f"A\n{args.A}", f"B\n{args.B}"]
    for s, label in enumerate(sector_labels):
        mid_angle = (s + 0.5) * (2 * np.pi / 3)
        # canvas coords before zoom: angle a → x=cos(a), y=-sin(a) (since angle=arctan2(-ys,xs))
        lx = (radius + 1.15 * radius * np.cos(mid_angle)) * 4
        ly = (radius - 1.15 * radius * np.sin(mid_angle)) * 4
        ax.text(lx, ly, label, ha="center", va="center", fontsize=7)

    ax.set_title(f"Disc centred at ({cx}, {cy}), radius {radius}px", fontsize=10)
    plt.tight_layout()
    plt.savefig(args.output, dpi=150, bbox_inches="tight")
    print(f"Saved plot to {args.output}")


if __name__ == "__main__":
    main()
