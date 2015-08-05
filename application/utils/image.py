from PIL import Image
from werkzeug.datastructures import FileStorage

COVER = 0
CONTAINE = 1

def thumbnail(image, width, height, position=('center', 'center'), fill=CONTAINE):
    try:
        if type(image) is FileStorage:
            image.seek(0)
        image = Image.open(image)
        owidth = image.size[0]
        oheight = image.size[1]

        wr, hr = 1.0*width/owidth, 1.0*height/oheight
        size = owidth, oheight
        x, y = position
        # back = Image.new('RGBA', (width, height), (125, 125, 125, 0))
        if fill == COVER:
            if wr < hr:
                size = owidth*height/oheight, height
            else:
                size = width, oheight*width/owidth
        else:
            if wr > hr:
                size = int(owidth*height/oheight), height
            else:
                size = width, oheight*width/owidth

        if x == 'center':
            x = (size[0] - width) / 2
        elif x == 'right':
            x = size[0] - width
        else:
            x = 0

        if y == 'center':
            y = (size[1] - height) / 2
        elif y == 'bottom':
            y = size[1] - height
        else:
            y = 0

        size = int(size[0]), int(size[1])
        x, y = int(x), int(y)
        width, height = int(width), int(height)

        image = image.resize(size, Image.ANTIALIAS)
        image = image.crop((x, y, x+width, y+height))
        return image

    except IOError as e:
        print(e.errno)
        print(e)
        print("Can not resize image ")


def resize(image, width=None, height=None, max_width=float("inf"), max_height=float("inf")):
    try:
        if type(image) is FileStorage:
            image.seek(0)
        image = Image.open(image)
        owidth = image.size[0]
        oheight = image.size[1]

        size = owidth, oheight
        if not width and owidth > max_width: width = max_width
        if not height and oheight > max_height: height = max_height
        if width is not None and height is not None:
            size = width, height
        elif width is not None:
            p = width/float(owidth)
            size = width, int(oheight*p)
        elif height is not None:
            p = height/float(oheight)
            size = int(owidth*p), height
        image = image.resize(size, Image.ANTIALIAS)
        if image.mode == 'RGBA':
            bg = Image.new(mode='RGBA', size=image.size, color=(255, 255, 255, 0))
            bg.paste(image, image)
            image = bg
        return image

    except IOError as e:
        print(e.errno)
        print(e)
        print("Can not resize image ")