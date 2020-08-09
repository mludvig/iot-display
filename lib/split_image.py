#!/usr/bin/env python3

from PIL import Image


def get_chunks(lst, n):
    while lst:
        ret, lst = lst[:n], lst[n:]
        yield ret


def split_image(img, color, match, nomatch):
    out = b''
    for chunk in get_chunks(img.tobytes(), 3):
        out += bytes(match) if set(chunk) == set(color) else bytes(nomatch)
    img_out = Image.frombytes(size=img.size, mode='RGB', data=out)
    return img_out


def bytes_to_bitmap(bts):
    out_array = []
    for chunk in get_chunks(bts, 8):
        out = 0
        for pixel in chunk:
            out |= bool(pixel)
            out <<= 1
        out_array.append(out>>1)
    return out_array


def image_to_epd_data(img):
    return bytes_to_bitmap(img.convert('L').transpose(Image.ROTATE_90).tobytes())


# Tests

def test_get_chunks():
    lst = list(range(20))
    chunks = list(get_chunks(lst, 3))
    assert len(chunks) == 7
    assert chunks[0] == [ 0, 1, 2 ]
    assert chunks[-1] == [ 18, 19 ]


def test_split_image():
    img = Image.open('tests/yes-c.png')
    img = img.convert('RGB')
    img_red_mask = split_image(img, (255, 0, 0), (255, 255, 255), (0, 0, 0))

    img_expected = Image.open('tests/red_mask.png')

    assert img_red_mask.tobytes() == img_expected.tobytes()


def test_bytes_to_bitmap():
    bts = b'\x00\x00\x00\xff\x00\xff\xff\xff\x00\x00\xff\x00\xff\xff\xff\x00'
    bitmap = bytes_to_bitmap(bts)
    assert bitmap == [ 0x17, 0x2e ]

def test_image_to_epd():
    import toml
    image_file = 'tests/2in13bc-ry.bmp'
    toml_file = 'tests/2in13bc-ry.toml'
    with open(toml_file, 'rt') as f:
        toml_data = toml.load(f)

    image = Image.open(image_file)
    epd_data = image_to_epd_data(image)

    assert epd_data == toml_data['epd_data_expected']
