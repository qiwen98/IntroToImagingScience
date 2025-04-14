from skimage.data import shepp_logan_phantom
from skimage.transform import resize


def create_phantom(size):
    phantom = shepp_logan_phantom()  # Default is 400x400
    phantom_resized = resize(phantom, (size, size), mode="reflect", anti_aliasing=True)

    return phantom_resized
