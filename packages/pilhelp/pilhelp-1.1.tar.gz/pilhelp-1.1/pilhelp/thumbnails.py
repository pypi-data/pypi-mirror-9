from PIL import Image, ImageOps


def thumbnail(img, width, height, crop_border_px=0, letterboxing=False,
    letterbox_color='black', method=Image.ANTIALIAS, ):
    """
    Resizes the image to `width` and `height` and returns the result as a
    instance of PIL.Image.Image.
    There are two ways of resizing that you define by leaving `letterboxing`
    set to False or setting it to True. Letterboxing means, that a picture,
    whose aspect ratio does not fit the requirements, will get borders to fit.
    Its color is defined by `letterbox_color`, black by default.
    Without letterboxing, the image gets cropped to fit.

    If the image has frayed borders (e.g. a still of a video) you can crop all
    sides by setting the amount of pixels as `crop_border_px`.
    """
    if crop_border_px:
        img = ImageOps.crop(img, border=crop_border_px)

    if letterboxing:
        img.thumbnail((width, height, ), resample=method)
        img_width, img_height = img.size
        if (img_width, img_height) != (width, height, ):
            bg = Image.new(img.mode, (width, height, ), letterbox_color)
            bounding_box = (
                int((width - img_width) / 2),
                int((height - img_height) / 2),
            )
            bg.paste(img, box=bounding_box)
            img = bg
    else:
        img = ImageOps.fit(img, (width, height, ), method=method)

    return img
