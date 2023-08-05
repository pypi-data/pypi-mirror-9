import os
import re
from PIL import Image


DENSITY_TYPES = ('ldpi', 'mdpi', 'hdpi', 'xhdpi', 'xxhdpi', 'xxxhdpi')
DENSITY_MAP = {
    'ldpi': float(3),
    'mdpi': float(4),
    'hdpi': float(6),
    'xhdpi': float(8),
    'xxhdpi': float(12),
    'xxxhdpi': float(16),
}


class AssetResizer():
    def __init__(self, out, source_density='xhdpi', prefix='', ldpi=False,
            xxxhdpi=False, image_filter=Image.ANTIALIAS, image_quality=None):
        if source_density not in DENSITY_TYPES:
            raise ValueError('source_density must be one of %s' % str(DENSITY_TYPES))

        self.out = os.path.abspath(out)
        self.source_density = source_density
        self.prefix = prefix
        self.ldpi = ldpi
        self.xxxhdpi = xxxhdpi
        self.image_filter = image_filter
        self.image_quality = image_quality

    def mkres(self):
        """
        Create a directory tree for the resized assets
        """
        for d in DENSITY_TYPES:
            if d == 'ldpi' and not self.ldpi:
                continue  # skip ldpi
            if d == 'xxxhdpi' and not self.xxxhdpi:
                continue  # skip xxxhdpi

            try:
                path = os.path.join(self.out, 'res/drawable-%s' % d)
                os.makedirs(path, 0755)
            except OSError:
                pass

    def get_out_for_density(self, target_density):
        """
        Return the out directory for the given target density
        """
        return os.path.join(self.out, 'res/drawable-%s' % target_density)

    def get_size_for_density(self, size, target_density):
        """
        Return the new image size for the target density
        """
        current_size = size
        current_density = DENSITY_MAP[self.source_density]
        target_density = DENSITY_MAP[target_density]

        return int(current_size * (target_density / current_density))

    def get_safe_filename(self, filename):
        """
        Return a sanitized image filename
        """
        return re.sub("@[0-9]+x", "", filename).replace('-', '_')

    def resize(self, path):
        """
        Generate assets from the given image
        """
        return self.resize_image(path, Image.open(path))

    def resize_image(self, path, im):
        """
        Generate assets from the given image and path in case you've already
        called Image.open
        """
        # Get the original filename
        _, filename = os.path.split(path)

        # Generate the new filename
        filename = self.get_safe_filename(filename)
        filename = '%s%s' % (self.prefix if self.prefix else '', filename)

        # Get the original image size
        w, h = im.size

        # Generate assets from the source image
        for d in DENSITY_TYPES:
            if d == 'ldpi' and not self.ldpi:
                continue  # skip ldpi
            if d == 'xxxhdpi' and not self.xxxhdpi:
                continue  # skip xxxhdpi

            out_file = os.path.join(self.out,
                    self.get_out_for_density(d), filename)

            if d == self.source_density:
                im.save(out_file, quality=self.image_quality)
            else:
                size = (self.get_size_for_density(w, d),
                        self.get_size_for_density(h, d))
                im.resize(size, self.image_filter).save(out_file,
                        quality=self.image_quality)
