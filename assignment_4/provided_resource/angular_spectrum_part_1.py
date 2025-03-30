import numpy as np
from numpy.fft import fft2, ifft2, fftshift, ifftshift

def padded_angular_spectrum(input_field, x_max_m, z_m, lambda_m, n_pad_pix):
    """
    Propagates an optical field using the Angular Spectrum method with padding.
    
    Parameters:
        input_field (ndarray): The input field (amplitude distribution).
        x_max_m (float): Maximum spatial extent (meters).
        z_m (float): Propagation distance (meters).
        lambda_m (float): Wavelength (meters).
        n_pad_pix (int): Number of pixels to pad.

    Returns:
        ndarray: Output field after propagation.
    """
    # Pad input field with zeros
    padded_input_field = np.pad(input_field, n_pad_pix, mode='constant')

    # Get sizes of padded and unpadded fields
    N_unpadded = input_field.shape[0]  # Assuming square input field
    N = padded_input_field.shape[0]  # Padded size

    # Compute spatial coordinates
    dx_m = 2 * x_max_m / (N_unpadded - 1)
    x_m = np.linspace(-(N - 1) * dx_m / 2, (N - 1) * dx_m / 2, N)

    # Compute frequency domain coordinates
    fx_max_pm = 1 / (2 * dx_m)  # Maximum frequency
    dfx_pm = 1 / (N * dx_m)  # Frequency step size

    if len(x_m) % 2 == 0:
        fx_pm = np.linspace(-fx_max_pm, fx_max_pm - dfx_pm, N)  # Even case
    else:
        fx_pm = np.linspace(-fx_max_pm, fx_max_pm, N)  # Odd case

    # Create frequency domain coordinate matrices
    kx_radpm = 2 * np.pi * fx_pm
    Kx_radpm, Ky_radpm = np.meshgrid(kx_radpm, kx_radpm)

    # Compute wavenumber
    k_radpm = 2 * np.pi / lambda_m

    # Compute transfer function (propagation kernel)
    kernel = np.exp(1j * z_m * np.sqrt(k_radpm**2 - Kx_radpm**2 - Ky_radpm**2))

    # Apply Angular Spectrum Method
    padded_input_fft = fftshift(fft2(padded_input_field))  # Forward FFT
    padded_output_fft = padded_input_fft * kernel  # Multiply by transfer function
    padded_output_field = ifft2(ifftshift(padded_output_fft))  # Inverse FFT

    # Crop out the original field size
    output_field = padded_output_field[n_pad_pix:n_pad_pix + N_unpadded,
                                       n_pad_pix:n_pad_pix + N_unpadded]

    return output_field