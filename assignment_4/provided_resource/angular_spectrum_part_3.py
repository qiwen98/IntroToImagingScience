import numpy as np

#########################################################
# Make the propagation distance a further away, try 100mm
#########################################################

# Angular Spectrum Method (Try popagating to at least 100mm with this version, experimental. Slightly broken)
def ASM(E_input,wavelength,dx,dy,propagation_distance,freqfilt=False):
    #  INPUT PARAMETERS
    #  E_input = A 2D complex matrix with the initial electric field
    #  wavelength, in mm 
    #  dx, dy = pixel size, in mm
    #  propagation_distance, in mm

    # Adding some padding
    pad = 2000
    E_input = np.pad(E_input, pad)
    [Ny, Nx] = E_input.shape
 
    # Fourier transform of the input E_input
    E_input_fft = np.fft.fft2(E_input)
    
    # Calculate the wave number, k space
    wave_number = 1/wavelength
    
    # Constructing the frequency grid
    kx = np.fft.fftshift(np.arange(-Nx/2,(Nx/2))/Nx/dx)
    ky = np.fft.fftshift(np.arange(-Ny/2,(Ny/2))/Ny/dy)
    [KX, KY] = np.meshgrid(kx, ky)
    # print(np.max(KX),np.max(KY),wave_number**2)


    # Kernel
    if not freqfilt:
        propagation_function = np.exp(1j*2*np.pi*(propagation_distance)*np.sqrt((wave_number**2 - KX**2 - KY**2)))
        propagation_function[np.isnan(propagation_function)] = 0

    else:
        #################################################################
        # Bandlimit the kernel
        # see band-limited ASM - Matsushima et al. (2009)
        # K. Matsushima and T. Shimobaba, 
        # "Band-Limited Angular Spectrum Method for Numerical Simulation of Free-Space Propagation in Far and Near Fields,"
        #  Opt. Express  17, 19662-19673 (2009).
        #################################################################
        K_lambda = 2*np.pi /  wavelength # T x C x H x W
        K_lambda_2 = K_lambda**2
        K2 = KX**2+KY**2
        ang = - propagation_distance * np.sqrt(K_lambda_2 - K2+0j) # T x C x H x W
        if np.iscomplexobj(ang):
            ang = ang.real
        # size of the field
        # # Total field size on the hologram plane
        length_x = Nx* dx 
        length_y = Ny  * dy

        # band-limited ASM - Matsushima et al. (2009)
        f_y_max = 2*np.pi / np.sqrt((2 * propagation_distance * (1 / length_x) ) **2 + 1) / wavelength
        f_x_max = 2*np.pi / np.sqrt((2 * propagation_distance * (1 / length_y) ) **2 + 1) / wavelength


        H_filter = np.zeros_like(ang)
        H_filter[ ( np.abs(KX) < f_x_max) & (np.abs(KY) < f_y_max) ] = 1


        propagation_function =  H_filter * np.exp(1j*H_filter * ang)
    
    #  Applying the filter in the Fourier domain
    E_input_fft_propagated = E_input_fft*propagation_function
    
    #  Inverse Fourier transform to obtain the propagated E_input
    E_input_propagated = np.fft.ifft2(E_input_fft_propagated)

    return E_input_propagated[pad:-pad,pad:-pad]
