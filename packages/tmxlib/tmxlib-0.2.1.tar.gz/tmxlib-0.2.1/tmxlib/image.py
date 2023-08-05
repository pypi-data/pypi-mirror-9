"""Image loading
----------------

The :func:`~tmxlib.image.open` function provides a high-level interface to
opening images, regardless

"""

from __future__ import division

_builtin_open = open

from tmxlib.image_base import Image, ImageRegion

image_classes = []
try:
    from tmxlib import image_pil
    image_classes.append(image_pil.PilImage)
except ImportError:
    pass

try:
    from tmxlib import image_png
    image_classes.append(image_png.PngImage)
except ImportError:
    pass

preferred_image_class = image_classes[0]

def open(filename, trans=None, size=None):
    """Open the given image file

    Uses ``preferred_image_class``.

    :param filename: Name of the file to load the image from
    :param trans:
        Optional color that should be rendered as transparent
        (this is not implemented yet)
    :param size:
        Optional (width, height) tuple.
        If specified, the file will not be read from disk when the image size
        needs to be known.
        If and when the image is loaded, the given size is checked and an
        exception is raised if it does not match.
    :return: An :class:`~tmxlib.image_base.Image`

    Note that the file is not opened until needed.
    This makes it possible to use maps and tilesets that refer to nonexistent
    images.
    """
    cls = preferred_image_class
    return cls(trans=trans, size=size, source=filename)
