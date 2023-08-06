# Input required: fit-box or fit-width or fit-height


class PuzzleImage(object):
    def __init__(self, original_width, original_height, width=None, height=None):
        """
        If both width and height are specified, it will fit the image within
        that size. Otherwise it will fit the image according the passed param.
        """
        if width is None and height is None:
            raise ValueError("You must specify a width or a height, or both.")
        self.original_width = original_width
        self.original_height = original_height
        self.requested_width = width
        self.requested_height = height
        self.final_width = None
        self.final_height = None
        self._fit()

    def _fit(self):
        """
        Adjusts the final_width and final_height appropriately
        """
        pass

    def draw_tile(self, tile, x, y):
        """
        Draw the tile in the final image where x, y is the top left corner of the
        tile in the image.
        """
        pass
