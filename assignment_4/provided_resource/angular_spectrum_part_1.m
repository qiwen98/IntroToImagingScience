%% Problem 4C solution - angular spectrum propagator
% Author: John Bass
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
    kernel = exp(1j * z_m * sqrt(k_radpm.^2 - Kx_radpm.^2 - Ky_radpm.^2));

    % Propagate the input field
    paddedInputField_fft = fftshift(fft2(paddedInputField));
    paddedOutputField_fft = paddedInputField_fft .* kernel;
    paddedOutputField = ifft2(ifftshift(paddedOutputField_fft));

    % Unpad input field
    outputField = paddedOutputField(nPad_pix+1:nPad_pix+size(inputField,1),...
                                   nPad_pix+1:nPad_pix+size(inputField,2));
end

% === Propagate point source to observation window (same size as diffuser) ===

% Define physical parameters
lambda_m = 500e-9;         % Wavelength [m]
z_m = 0.5;                 % Propagation distance [m]
x_max_m = 37.5e-3;         % Half-width of the observation window [m] → full window = 75 mm
N = 1001;                  % Resolution of field (un-padded)
nPad_pix = N;              % Padding to prevent wraparound artifacts

% Create spatial grid for field definition
dx_m = 2 * x_max_m / (N - 1);
x_m = linspace(-x_max_m, x_max_m, N);
[X, Y] = meshgrid(x_m, x_m);

% Define field arriving at z = 0 from a point source at z = -z_m
R = sqrt(X.^2 + Y.^2 + z_m^2);
inputField = exp(1j * 2 * pi * R / lambda_m) ./ R;

% Propagate field to distance z_m using original function
outputField = paddedAngularSpectrum(inputField, x_max_m, z_m, lambda_m, nPad_pix);

% Display phase of the propagated field
figure;
imagesc(x_m*1e3, x_m*1e3, angle(outputField));
axis image;
xlabel('x (mm)');
ylabel('y (mm)');
title('Phase at Observation Window (75 mm wide)');
colorbar;
