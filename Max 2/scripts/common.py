from PIL import Image
import numpy as np
MAX2 = '/home/claude/max2/'
def half(f, side):
    """side 'L' or 'R' — половина разворота на белом фоне"""
    s = Image.open(f'{MAX2}IMG_{f}.png').convert('RGBA')
    im = s.crop((0, 0, 2588, 2625)) if side == 'L' else s.crop((2588, 0, 5175, 2625))
    bg = Image.new('RGBA', im.size, 'white'); bg.alpha_composite(im)
    return bg.convert('RGB')
