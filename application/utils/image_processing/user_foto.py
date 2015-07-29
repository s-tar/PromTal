from uuid import uuid1
import os
from PIL import Image
#sudo apt-get install libjpeg-dev
#pip install -I pillow


class NotImage(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


def makedirs(path_list):
    path_new = ''
    for path in path_list:
        path_new = os.path.join(path_new, path)
        if not os.path.isdir(path_new):
            os.mkdir(path_new)
    return path_new


def delete_files(path_walk):
    for root, dirs, files in os.walk(path_walk):
        for name in files:
            fullname = os.path.join(root, name)
            os.remove(fullname)


def imageResize(data, output_size):
    image = Image.open(data)
    m_width = float(output_size[0])
    m_height = float(output_size[1])
    if image.mode not in ('L', 'RGB'):
        image = image.convert('RGB')
    w_k = image.size[0]/m_width
    h_k = image.size[1]/m_height
    if output_size < image.size:
        if w_k > h_k:
            new_size = (m_width, image.size[1]/w_k)
        else:
            new_size = (image.size[0]/h_k, m_height)
    else:
        new_size = image.size
    new_size = tuple(map(int, new_size))
    return image.resize(new_size,Image.ANTIALIAS)


def save_user_fotos(file, current_user, avatar=False):
    try:
        im = Image.open(file)
    except OSError:
        raise NotImage('Not image')
    path_list = ["application", "files", "users", str(current_user.id)]
    if avatar:
        path_list.append("avatar")
    path_walk = makedirs(path_list)
    if avatar:
        delete_files(path_walk)
    uid = ''.join(str(uuid1()).split('-'))
    name = "{}_{}".format(uid, file.filename)
    name_small = "{}_s_{}".format(uid, file.filename)
    output_size = 300, 300
    output_size_small = 50, 50
    def save_resize_foto(file, output_size, name):
        im = imageResize(file, output_size)
        img_path = os.path.join(path_walk, name)
        im.save(img_path, 'JPEG', quality=85)
    save_resize_foto(file, output_size, name)
    save_resize_foto(file, output_size_small, name_small)
    return name, name_small