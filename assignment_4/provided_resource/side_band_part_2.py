import numpy as np
import matplotlib.pyplot as plt


""" Variable Fields """
num_pixels = 40
FT_img = None # TODO: Load the FT image here
R = 20 # Radius of the circle in the FT image
""" End of Variable Fields """

""" Sample code for shifting side band for Part 2 """
# 1) Horizontal crop (the circle on the right side)
FT_horiz_OX_shift = -1205 # We move the image certain pixels to the right (or left, if negative)
FT_horiz_OY_shift = -50   # We move the image certain pixels

# 2) Shift the image
def shifting(FT_img, shift_OX, shift_OY):
    left_OX = 0 if shift_OX < 0 else shift_OX
    right_OX = shift_OX if shift_OX < 0 else num_pixels
    L_OX = -shift_OX if shift_OX < 0 else 0
    R_OX = num_pixels if shift_OX < 0 else num_pixels - shift_OX

    left_OY = 0 if shift_OY < 0 else shift_OY
    right_OY = shift_OY if shift_OY < 0 else num_pixels
    L_OY = -shift_OY if shift_OY < 0 else 0
    R_OY = num_pixels if shift_OY < 0 else num_pixels - shift_OY

    FT_shift = np.zeros_like(FT_img)
    FT_shift[left_OY:right_OY, left_OX:right_OX] = FT_img[L_OY:R_OY, L_OX:R_OX]

    return FT_shift

FT_horiz_1 = shifting(FT_img, FT_horiz_OX_shift, FT_horiz_OY_shift)


""" Sample code for filtering side band for Part 2 """
# Create a centered circular Hanning window
sigma = R/2
center = num_pixels // 2

# Create a 2D Gaussian window
y, x = np.ogrid[-center:num_pixels-center, -center:num_pixels-center]
distance_from_center_squared = x*x + y*y
FT_filter = np.exp(-distance_from_center_squared / (2 * sigma * sigma))

# Apply the filter
FT_horiz_filtered_1 = FT_horiz_1 * FT_filter

# normalization helper function
def normalize(x):
    x = np.nan_to_num((x - np.nanmin(x))/(np.nanmax(x) - np.nanmin(x)), nan=np.nan)
    return x

# Plot
with np.errstate(divide='ignore'):
    FT_horiz_filtered_plot = np.log10(20 * np.abs(FT_horiz_filtered_1) + 1e-5)
    # Assuming normalize is a function defined elsewhere in your code
    FT_horiz_filtered_plot = normalize(FT_horiz_filtered_plot)


plt.title("Horizontally shifted and filtered FT image")
with np.errstate(divide='ignore'):
    plt.imshow(FT_horiz_filtered_plot, cmap='viridis')
plt.colorbar()
plt.xlabel("Spatial frequencies $f_x$")
plt.ylabel("Spatial frequencies $f_y$")
plt.show()
