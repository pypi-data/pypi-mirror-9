from frasco import Feature, action, OptionMissingError, AttrDict, current_app
from PIL import Image
import os


class ImagesFeature(Feature):
    name = "images"
    defaults = {"search_dir": None,
                "dest_dir": None,
                "output_format": None}

    def init_app(self, app):
        default_dir = None
        if "forms" in app.features:
            default_dir = app.features.forms.options["upload_dir"]
        else:
            default_dir = app.static_folder

        if not self.options["search_dir"]:
            self.options["search_dir"] = default_dir
        if not self.options["dest_dir"]:
            self.options["dest_dir"] = default_dir

    def get_path(self, filename):
        if os.path.isabs(filename):
            return filename
        sdir = self.options["search_dir"]
        if sdir:
            f = os.path.join(sdir, filename)
            if os.path.exists(f):
                return f
        return filename

    def get_dest_filename(self, path, opts, default="{path}{prefix}{name}{suffix}{ext}", **kwargs):
        dest = opts.get("dest", default)
        dest_dir = opts.get("dest_dir", self.options["dest_dir"])
        if "{" in dest:
            filename, ext = os.path.splitext(path)
            data = dict(path=os.path.dirname(filename), name=os.path.basename(filename),
                        filename=filename, ext=ext, prefix="", suffix="")
            data.update(kwargs)
            data.update(dict((k, opts[k]) for k in ("ext", "prefix", "suffix") if k in opts))
            dest = dest.format(**data)
        if not os.path.isabs(dest) and dest_dir:
            return os.path.join(dest_dir, dest), dest
        return dest, dest

    def save_img(self, path, opts, img, **kwargs):
        pathname, filename = self.get_dest_filename(path, opts, **kwargs)
        img.save(pathname, opts.get("format", self.options["output_format"]))
        return filename

    def get_size(self, opts, lprefix="", sprefix="", ratio=None):
        w = opts.get("%swidth" % lprefix, opts.get("%sw" % sprefix))
        h = opts.get("%sheight" % lprefix, opts.get("%sh" % sprefix))
        if ("%ssize" % lprefix) in opts:
            w, h = map(int, opts["%ssize" % lprefix].split("x", 1))
        if ((w is None or h is None) and not ratio) or (w is None and h is None):
            raise OptionMissingError("Missing size options for image manipulation")
        if w is None:
            r = float(h) / float(ratio[1])
            w = int(ratio[0] * r)
        elif h is None:
            r = float(w) / float(ratio[0])
            h = int(ratio[1] * r)
        return w, h

    @action(default_option="path", as_="image")
    def read_image(self, path):
        img = Image(self.get_path(path))
        return AttrDict(format=img.format, size=img.size, mode=img.mode)

    @action("resize_image")
    def resize(self, path, resample=Image.ANTIALIAS, **opts):
        path = self.get_path(path)
        img = Image.open(path)

        keep_ratio = False
        try:
            size = self.get_size(opts)
        except OptionMissingError:
            size = self.get_size(opts, "max_", "m", ratio=img.size)
            keep_ratio = True

        if keep_ratio:
            img.thumbnail(size, resample)
        else:
            img = img.resize(size, resample)

        return self.save_img(path, opts, img, suffix="-%sx%s" % size)

    @action("create_image_thumbnail", default_option="path")
    def create_thumbnail(self, path, resample=Image.ANTIALIAS, **opts):
        img = Image.open(self.get_path(path))

        fixed_size = False
        try:
            size = self.get_size(opts)
            fixed_size = True
        except OptionMissingError:
            size = self.get_size(opts, "max_", "m", ratio=img.size)

        if fixed_size and size[0] < img.size[0] and size[1] < img.size[1]:
            r = max(float(size[0]) / float(img.size[0]), float(size[1]) / float(img.size[1]))
            isize = (int(img.size[0] * r), int(img.size[1] * r))
            img = img.resize(isize, resample)
            x = max((isize[0] - size[0]) / 2, 0)
            y = max((isize[1] - size[1]) / 2, 0)
            img = img.crop((x, y, size[0], size[1]))
        else:
            img.thumbnail(size, resample)

        return self.save_img(path, opts, img, suffix="-thumb-%sx%s" % size)

    @action("crop_image")
    def crop(self, path, **opts):
        box = opts.get("box")
        if not box:
            w = opts.get("width", opts.get("w"))
            h = opts.get("height", opts.get("h"))
            box = (opts.get("x", 0), opts.get("y", 0), w, h)
        path = self.get_path(path)
        img = Image.open(path)
        img = img.crop(box)
        return self.save_img(path, opts, img, suffix="-cropped")

    @action("rotate_image")
    def rotate(self, path, angle, resample=0, expand=0, **opts):
        path = self.get_path(path)
        img = Image(path)
        img = img.rotate(float(angle), resample, expand)
        return self.save_img(path, opts, img, suffix="-rotated")

    @action("transpose_image")
    def transpose(self, path, method, **opts):
        mapping = {"flip_left_right": Image.FLIP_LEFT_RIGHT,
                   "flip_top_bottom": Image.FLIP_TOP_BOTTOM,
                   "rotate90": Image.ROTATE_90,
                   "rotate180": Image.ROTATE_180,
                   "rotate270": Image.ROTATE_270}
        path = self.get_path(path)
        img = Image.open(path)
        img = img.transpose(mapping[method])
        return self.save_img(path, opts, img, suffix="-" + method)

    @action("add_image_watermark")
    def add_watermark(self, path, watermark, **opts):
        path = self.get_path(path)
        img = Image.open(path)
        wtmk = Image.open(watermark)
        iw, ih = img.size
        ww, wh = wtmk.size
        pos = (opts.get("x", iw - ww), opts.get("y", ih - wh))
        img.paste(wtmk, pos)
        return self.save_img(path, opts, img, suffix="-watermark")