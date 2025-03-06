import argparse
from PIL import Image
import numpy as np

#   ⠀ ⢀ ⠠ ⢠ ⠐ ⢐ ⠰ ⢰ ⠈ ⢈ ⠨ ⢨ ⠘ ⢘ ⠸ ⢸
#   ⡀ ⣀ ⡠ ⣠ ⡐ ⣐ ⡰ ⣰ ⡈ ⣈ ⡨ ⣨ ⡘ ⣘ ⡸ ⣸
#   ⠄ ⢄ ⠤ ⢤ ⠔ ⢔ ⠴ ⢴ ⠌ ⢌ ⠬ ⢬ ⠜ ⢜ ⠼ ⢼
#   ⡄ ⣄ ⡤ ⣤ ⡔ ⣔ ⡴ ⣴ ⡌ ⣌ ⡬ ⣬ ⡜ ⣜ ⡼ ⣼
#   ⠂ ⢂ ⠢ ⢢ ⠒ ⢒ ⠲ ⢲ ⠊ ⢊ ⠪ ⢪ ⠚ ⢚ ⠺ ⢺
#   ⡂ ⣂ ⡢ ⣢ ⡒ ⣒ ⡲ ⣲ ⡊ ⣊ ⡪ ⣪ ⡚ ⣚ ⡺ ⣺
#   ⠆ ⢆ ⠦ ⢦ ⠖ ⢖ ⠶ ⢶ ⠎ ⢎ ⠮ ⢮ ⠞ ⢞ ⠾ ⢾
#   ⡆ ⣆ ⡦ ⣦ ⡖ ⣖ ⡶ ⣶ ⡎ ⣎ ⡮ ⣮ ⡞ ⣞ ⡾ ⣾
#   ⠁ ⢁ ⠡ ⢡ ⠑ ⢑ ⠱ ⢱ ⠉ ⢉ ⠩ ⢩ ⠙ ⢙ ⠹ ⢹
#   ⡁ ⣁ ⡡ ⣡ ⡑ ⣑ ⡱ ⣱ ⡉ ⣉ ⡩ ⣩ ⡙ ⣙ ⡹ ⣹
#   ⠅ ⢅ ⠥ ⢥ ⠕ ⢕ ⠵ ⢵ ⠍ ⢍ ⠭ ⢭ ⠝ ⢝ ⠽ ⢽
#   ⡅ ⣅ ⡥ ⣥ ⡕ ⣕ ⡵ ⣵ ⡍ ⣍ ⡭ ⣭ ⡝ ⣝ ⡽ ⣽
#   ⠃ ⢃ ⠣ ⢣ ⠓ ⢓ ⠳ ⢳ ⠋ ⢋ ⠫ ⢫ ⠛ ⢛ ⠻ ⢻
#   ⡃ ⣃ ⡣ ⣣ ⡓ ⣓ ⡳ ⣳ ⡋ ⣋ ⡫ ⣫ ⡛ ⣛ ⡻ ⣻
#   ⠇ ⢇ ⠧ ⢧ ⠗ ⢗ ⠷ ⢷ ⠏ ⢏ ⠯ ⢯ ⠟ ⢟ ⠿ ⢿
#   ⡇ ⣇ ⡧ ⣧ ⡗ ⣗ ⡷ ⣷ ⡏ ⣏ ⡯ ⣯ ⡟ ⣟ ⡿ ⣿

def chunk_to_braille(chunk):
    positions = [(0, 0), (1, 0), (2, 0), (0, 1), (1, 1), (2, 1), (3, 0), (3, 1)]
    code = 0x2800
    for i, (row, col) in enumerate(positions):
            code += (chunk[row][col] << i)
    return chr(code)

def array_to_braille(arr):
    height, width = len(arr), len(arr[0])
    braille_lines = []

    for row in range(0, height, 4):
        braille_line = []

        for col in range(0, width, 2):
            chunk = [[arr[r][c] if r < height and c < width else 0
                      for c in range(col, col + 2)]
                     for r in range(row, row + 4)]

            braille_line.append(chunk_to_braille(chunk))

        braille_lines.append("".join(braille_line))

    return "\n".join(braille_lines)

def adjust_height(width, original_width, original_height):
    new_height = int((original_height / original_width) * width)
    return new_height + (4 - new_height % 4) % 4


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generates a ascii art from an image using braile symbols.')
    parser.add_argument('--img', help='Path to image file', required=True)
    parser.add_argument('--threshold', type=int, default=128, help='Threshold for binarization (0-255, lower = darker, higher = lighter)')
    parser.add_argument('--width', type=int, default=92, help='Max width')

    args = parser.parse_args()

    with Image.open(args.img) as img:
        img = img.convert("L")
        img = img.point(lambda x: 255 if x > args.threshold else 0, mode="1")


        width = args.width
        height = adjust_height(width, img.width, img.height)
        img = img.resize((width,height))

        pixels = np.asarray(img)
        print(array_to_braille(pixels))

