"""
Utilities for image manipulation.
"""
import copy
import png

# Python 2 / 3 compatibility
import sys
from applitools.errors import EyesError

if sys.version < '3':
    range = xrange


def png_image_from_file(f):
    """
    Reads the PNG data from the given file stream and returns a new PngImage instance.
    """
    width, height, pixels_iterable, meta_info = png.Reader(file=f).asDirect()
    return PngImage(width, height, list(pixels_iterable), meta_info)


def png_image_from_bytes(png_bytes):
    """
    Reads the PNG data from the given file stream and returns a new PngImage instance.
    """
    width, height, pixels_iterable, meta_info = png.Reader(bytes=png_bytes).asDirect()
    return PngImage(width, height, list(pixels_iterable), meta_info)


class PngImage(object):
    """
    Encapsulates an image.
    """

    def __init__(self, width, height, pixels, meta_info):
        """
        Initializes a PngImage object.
        The "pixels" argument should be a sequence of rows, where each row is a sequence of
        values representing pixels (no separation between pixels inside the raw).
        """
        self.width = width
        self.height = height
        self.pixels = pixels
        self.meta_info = meta_info
        # Images are either RGB or Greyscale
        if not meta_info["greyscale"]:
            self.pixel_size = 3
        else:
            self.pixel_size = 1
        # If there's also an alpha channel
        if meta_info["alpha"]:
            self.pixel_size += 1

    def paste(self, left, top, new_pixels):
        """
        Pastes the given pixels on the image. Expands width/height if needed. Pixel size must be
        the same as the current image's pixels.
        """
        x_start = left * self.pixel_size
        new_pixels_bytes_len = len(new_pixels[0])
        for y_offset in range(len(new_pixels)):
            y_current = top + y_offset
            # It's okay to use self.height as a condition, even after y_current is greater
            # than it, since in this case we append to the end of the list anyway.
            if y_current < self.height:
                original_row = self.pixels[y_current]
                updated_row = original_row[:x_start] + new_pixels[y_offset] + \
                    original_row[(x_start + new_pixels_bytes_len):]
                self.pixels[y_current] = updated_row
            else:
                self.pixels.append(new_pixels[y_offset])
        # Update the width and height if required
        paste_right = (x_start + new_pixels_bytes_len) / self.pixel_size
        self.width = max(self.width, paste_right)
        self.height = len(self.pixels)

    def get_subimage(self, region):
        """
        Returns a PNG binary.
        """
        if region.is_empty():
            raise EyesError('region is empty!')
        result_pixels = []
        x_start = region.left * self.pixel_size
        x_end = x_start + (region.width * self.pixel_size)
        y_start = region.top
        for y_offset in range(region.height):
            pixels_row = self.pixels[y_start + y_offset][x_start:x_end]
            result_pixels.append(pixels_row)
        meta_info = copy.copy(self.meta_info)
        meta_info['size'] = (region.width, region.height)
        return PngImage(region.width, region.height, result_pixels, meta_info)

    def remove_columns(self, left, count):
        """
        Removes pixels columns from the image.
        Args:
            left: The index of the left most column to remove.
            count: The number of columns to remove.
        """
        for row_index in range(self.height):
            self.pixels[row_index] = self.pixels[row_index][:(left * self.pixel_size)] + \
                self.pixels[row_index][(left + count) * self.pixel_size:]
            # Updating the width
            self.width = len(self.pixels[0]) / self.pixel_size

    def remove_rows(self, top, count):
        """
        Removes pixels rows from the image.
        Args:
            top: The index of the top most row to remove.
            count: The number of rows to remove.
        """
        self.pixels = self.pixels[:top] + self.pixels[(top + count):]
        self.height = len(self.pixels)

    def write(self, output):
        """
        Writes the png to the output stream.
        """
        self.meta_info['size'] = (self.width, self.height)
        png.Writer(**self.meta_info).write(output, self.pixels)