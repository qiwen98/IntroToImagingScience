function outputField = paddedAngularSpectrum(inputField,x_max_m,z_m,lambda_m,nPad_pix)
    % Pad input field
    paddedInputField = zeros(size(inputField)+2*nPad_pix);
    paddedInputField(nPad_pix+1:nPad_pix+size(inputField,1),...
                     nPad_pix+1:nPad_pix+size(inputField,2)) = inputField;

    % Save pixel side length of input field, for use later
    N_unpadded = size(inputField,1);
    N = size(paddedInputField,1);

    % Get spatial domain coordinate system
    dx_m = 2*x_max_m / (N_unpadded-1);
    x_m = -(N-1)*dx_m/2:dx_m:(N-1)*dx_m/2;

    % Get fourier-domain coordinate array. Even-length frames go up to a
    % different max frequency, and thus must be treated differently. See:
    % https://www.mathworks.com/help/matlab/ref/fft.html, "Noisy Signal"
    % example
    fx_max_pm = 1/dx_m/2;
    dfx_pm = 1/dx_m/N;
    if(mod(length(x_m),2)==0)
        fx_pm = linspace(-fx_max_pm,fx_max_pm-dfx_pm,N);
    else
        fx_pm = linspace(-fx_max_pm,fx_max_pm,N);
    end

    % Get frequency-domain coordinate matrices
    kx_radpm = 2 * pi * fx_pm;
    [Kx_radpm,Ky_radpm] = meshgrid(kx_radpm,kx_radpm);

    % Get wavenumber
    k_radpm = 2 * pi / lambda_m;

    % Define kernel function
    % CHANGED THIS
    sqrt_arg = k_radpm.^2 - Kx_radpm.^2 - Ky_radpm.^2 + 1e-20i;
    kernel = fftshift(exp(1j * z_m * sqrt(sqrt_arg)));

    % Propagate the input field
    paddedInputField_fft = fftshift(fft2(paddedInputField));
    paddedOutputField_fft = paddedInputField_fft .* kernel;
    paddedOutputField = ifft2(ifftshift(paddedOutputField_fft));

    % Unpad input field
    outputField = paddedOutputField(nPad_pix+1:nPad_pix+size(inputField,1),...
                                   nPad_pix+1:nPad_pix+size(inputField,2));
end

