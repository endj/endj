from PIL import Image, ImageStat
from os import listdir, mkdir
import sys
from math import sqrt
import os.path
import argparse
import requests
import json
from typing import List, Tuple
import time

GITHUB_EMOJI_API = 'https://api.github.com/emojis'


def produce_emoji_table(image_path: str, output_path: str, size: int, emoji_folder_path: str) -> str:
    image_scaled = resize_image(load_image(image_path), size)
    save_emojis(emoji_folder_path)
    dominant_emoji_colours = calculate_dominant_emoji_colours(
        emoji_folder_path)
    average_emoji_colours = caclulate_average_emoji_colours(emoji_folder_path)

    md1_rows = create_md(dominant_emoji_colours, image_scaled, size)
    md2_rows = create_md(average_emoji_colours, image_scaled, size)

    dump_md_rows_to_file('md1', md1_rows)
    dump_md_rows_to_file('md2', md2_rows)


def dump_md_rows_to_file(filename: str, rows):
    with open(filename, 'w') as file:
        for row in rows:
            file.write(row)
            file.write('\n')


def create_md(emoji_color_dict: dict, image_scaled: Image, size: int) -> str:
    table_rows = []
    width, height = image_scaled.size
    orig_pixel_map = image_scaled.load()

    for y in range(height):
        row = []
        for x in range(width):
            pixel = orig_pixel_map[x, y]
            r, g, b = pixel
            closest = ('', sys.maxsize)
            for (k, v) in emoji_color_dict.items():
                cr, cg, cb = v
                diff = sqrt(abs(r - cr)**2 + abs(g - cg)**2 + abs(b - cb)**2)
                if diff < closest[1]:
                    closest = (k, diff)
            row.append(closest[0])
        table_rows.append(row)
    return convert_table_rows_to_md_format(table_rows)


def convert_table_rows_to_md_format(table_rows):
    rows = []
    header = '|-'*len(table_rows) + '|'
    for row in table_rows:
        rows.append('|' + '|'.join([' :' + x + ': ' for x in row]) + '|')
    rows.insert(1, header)
    return rows


def save_emojis(emoji_folder_path: str):
    cached_emojis = set()
    if os.path.isdir(emoji_folder_path):
        cached_emojis = load_local_emojis(emoji_folder_path)
    else:
        os.mkdir(emoji_folder_path)

    available_emojis = get_available_github_emojis()
    emojis_to_download = compute_diff(cached_emojis, available_emojis)

    print(f'Found emojis not availabe localy {emojis_to_download}')
    fetch_emojis(emojis_to_download, emoji_folder_path)


def calculate_dominant_emoji_colours(emoji_folder_path: str) -> dict:
    emojis = load_local_emojis(emoji_folder_path)
    return_dict = dict()
    for emoji in emojis:
        image = load_image(f'{emoji_folder_path}/{emoji}')
        colour = get_dominant_colour(image)
        return_dict[emoji] = colour
    return return_dict


def caclulate_average_emoji_colours(emoji_folder_path: str) -> dict:
    emojis = load_local_emojis(emoji_folder_path)
    return_dict = dict()
    for emoji in emojis:
        image = load_image(f'{emoji_folder_path}/{emoji}')
        colour = get_average_colour(image)
        return_dict[emoji] = colour
    return return_dict


def get_dominant_colour(image: Image):
    colour_partitioned = image.convert('RGB').convert(
        'P', palette=Image.ADAPTIVE, colors=16)
    palette = colour_partitioned.getpalette()
    color_counts = sorted(colour_partitioned.getcolors(), reverse=True)
    palette_index = color_counts[0][1]
    result = palette[palette_index*3:palette_index*3+3]
    if result == [255, 255, 255] or result == [0, 0, 0]:
        palette_index = color_counts[1][1]
        return palette[palette_index*3:palette_index*3+3]
    else:
        return result


def get_average_colour(image: Image):
    avg = ImageStat.Stat(image).median[:-1]
    if len(avg) < 3:
        return [0, 0, 0]
    return avg


def load_image(image_path: str) -> Image:
    return Image.open(image_path)


def resize_image(img: Image, size: int) -> Image:
    return img.resize((size, size), Image.ANTIALIAS)


def get_available_github_emojis():
    response = requests.get(url=GITHUB_EMOJI_API, headers={
        'Accept': 'application/vnd.github.v3+json'})
    response.raise_for_status()
    return json.loads(response.text)


def load_local_emojis(path: str) -> set:
    return set(listdir(path))


def compute_diff(cached_emojis: set, available_emojis):
    diff = []
    for (k, v) in available_emojis.items():
        if not cached_emojis:
            diff.append((k, v))
        elif k not in cached_emojis:
            diff.append((k, v))
    return diff


def fetch_emojis(emojis_to_download: List[Tuple], output_folder: str):
    for emoji in emojis_to_download:
        content = download_emoji(emoji[1])
        if content != None:
            print(f'Downloading {emoji[0]} from {emoji[1]}')
            with open(f'{output_folder}/{emoji[0]}', 'wb+') as file:
                file.write(content)


def download_emoji(url: str):
    data = requests.get(url, timeout=5)
    if data.status_code == 404:
        print(f'Could not find {url} 404')
        return None
    data.raise_for_status()
    return data.content


parser = argparse.ArgumentParser(description='Produce emoji MD table.')
parser.add_argument('-p', help='Path to image file', required=True)
parser.add_argument('-o', help='Path to md output file', default='output.md')
parser.add_argument('-s', help='Table resolution width', default=16)
parser.add_argument('-e', help='Path to folder of emojis', default='emojis')

args = parser.parse_args()

md_emoji_table = produce_emoji_table(args.p, args.o, args.s, args.e)
