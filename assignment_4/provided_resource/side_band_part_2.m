% Variable Fields
num_pixels = 40;
FT_img = []; % TODO: Load the FT image here
R = 20; % Radius of the circle in the FT image
% End of Variable Fields

%% Sample code for shifting side band for Part 2
function FT_shift = shifting(FT_img, shift_OX, shift_OY, num_pixels)
    left_OX = 0;
    right_OX = num_pixels;
    L_OX = 1;
    R_OX = num_pixels;

    if shift_OX < 0
        left_OX = 1;
        right_OX = num_pixels + shift_OX;
        L_OX = 1 - shift_OX;
        R_OX = num_pixels;
    else
        left_OX = 1 + shift_OX;
        right_OX = num_pixels;
        L_OX = 1;
        R_OX = num_pixels - shift_OX;
    end

    left_OY = 0;
    right_OY = num_pixels;
    L_OY = 1;
    R_OY = num_pixels;

    if shift_OY < 0
        left_OY = 1;
        right_OY = num_pixels + shift_OY;
        L_OY = 1 - shift_OY;
        R_OY = num_pixels;
    else
        left_OY = 1 + shift_OY;
        right_OY = num_pixels;
        L_OY = 1;
        R_OY = num_pixels - shift_OY;
    end

    FT_shift = zeros(size(FT_img));
    FT_shift(left_OY:right_OY, left_OX:right_OX) = FT_img(L_OY:R_OY, L_OX:R_OX);
end

% Horizontal crop (the circle on the right side)
FT_horiz_OX_shift = -1205; % We move the image certain pixels to the right (or left, if negative)
FT_horiz_OY_shift = -50;   % We move the image certain pixels

% Shift the image
FT_horiz_1 = shifting(FT_img, FT_horiz_OX_shift, FT_horiz_OY_shift, num_pixels);

%% Sample code for filtering side band for Part 2
% Create a centered circular Hanning window
sigma = R / 2;
center = floor(num_pixels / 2);

% Create a 2D Gaussian window
[y, x] = ndgrid(-center:num_pixels-center-1, -center:num_pixels-center-1);
distance_from_center_squared = x.^2 + y.^2;
FT_filter = exp(-distance_from_center_squared / (2 * sigma^2));

% Apply the filter
FT_horiz_filtered_1 = FT_horiz_1 .* FT_filter;

% Normalization function
function x = normalize(x)
    x = (x - min(x(:))) / (max(x(:)) - min(x(:)));
end

% Plotting
FT_horiz_filtered_plot = log10(20 * abs(FT_horiz_filtered_1) + 1e-5);
FT_horiz_filtered_plot = normalize(FT_horiz_filtered_plot);

figure;
imagesc(FT_horiz_filtered_plot);
colormap('viridis');
colorbar;
title('Horizontally shifted and filtered FT image');
xlabel('Spatial frequencies $f_x$', 'Interpreter', 'latex');
ylabel('Spatial frequencies $f_y$', 'Interpreter', 'latex');