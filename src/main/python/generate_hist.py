import numpy as np
import matplotlib
# Force the non-interactive backend for headless environments
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import OpenImageIO as oiio
import argparse
import sys
import os

def generate_exr_histogram(input_path, output_path):
    # 1. Open and Validate the EXR
    if not os.path.exists(input_path):
        print(f"Error: Input file '{input_path}' not found.")
        sys.exit(1)

    img = oiio.ImageInput.open(input_path)
    if not img:
        print(f"Error: Could not open {input_path}. {oiio.geterror()}")
        sys.exit(1)

    spec = img.spec()
    pixels = img.read_image("float")
    img.close()

    # 2. Reshape and Clean Data
    # Flatten to (Pixels, Channels) and take the first 3 (RGB)
    pixels = pixels.reshape(-1, spec.nchannels)[:, :3]
    
    # Remove non-finite values (NaN, Inf) and floor at 1e-6 to avoid log(0)
    pixels = pixels[np.all(np.isfinite(pixels), axis=1)]
    pixels = np.maximum(pixels, 1e-6)

    # 3. Setup the Plot
    plt.figure(figsize=(12, 7))
    colors = ['#e74c3c', '#2ecc71', '#3498db']
    labels = ['Red', 'Green', 'Blue']
    
    # Generate 200 log-spaced bins between min and max
    bins = np.logspace(np.log10(np.min(pixels)), np.log10(np.max(pixels)), 200)

    for i in range(3):
        plt.hist(pixels[:, i], bins=bins, color=colors[i], 
                 alpha=0.5, label=labels[i], histtype='stepfilled')

    # Visual aids for HDR analysis
    plt.axvline(x=1.0, color='black', linestyle='--', alpha=0.3, label='SDR White (1.0)')
    
    # Log scale for x-axis is the gold standard for linear light data
    plt.xscale('log')
    
    plt.title(f"HDR RGB Distribution: {os.path.basename(input_path)}")
    plt.xlabel("Linear Intensity (Stops/Values)")
    plt.ylabel("Pixel Count")
    plt.legend()
    plt.grid(True, which="both", ls="-", alpha=0.1)

    # 4. Save to the second positional argument
    try:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Success: Histogram saved to '{output_path}'")
    except Exception as e:
        print(f"Error saving output: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Defining positional arguments
    parser = argparse.ArgumentParser(description="Convert an EXR's RGB data into a PNG histogram.")
    parser.add_argument("input", help="Source .exr file path")
    parser.add_argument("output", help="Destination .png file path")
    
    args = parser.parse_args()
    generate_exr_histogram(args.input, args.output)