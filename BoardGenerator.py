import StringIO
import random
from PIL import Image, ImageDraw, ImageFont


def generate_board(cards):
    """
    Takes a list of card names like ["OneRedSolidSquiggle", ...]

    Returns a filename of the generated image
    """

    # numbers = ['One', 'Two', 'Three']
    # colors = ['Red', 'Green', 'Purple']
    # shadings = ['Solid', 'Shaded', 'Hollow']
    # shapes = ['Squiggle', 'Oval', 'Diamond']

    assert len(cards) % 3 == 0, 'Must pass a list of cards with length \
    that\'s a multiple of 3'

    num_rows = len(cards) / 3

    canvas = Image.new('RGB', ((160+20)*3, (100+10)*num_rows-10), 'white')

    fnt = ImageFont.truetype('./Arial.ttf', 24)
    d = ImageDraw.Draw(canvas)

    i = 0
    for row in range(num_rows):
        for col in range(3):
            im = Image.open('cards/Card{}.png'.format(
                cards[i]
            ))
            canvas.paste(im, ((160+20)*col+20, (100+10)*row))
            d.text(((160+20)*col+10,(100+10)*row+5), chr(i+65), font=fnt, fill=(0,0,0,255))
            i += 1

    output = StringIO.StringIO()
    canvas.save(output, format='png')
    output_string = output.getvalue()
    output.close()

    return output_string
