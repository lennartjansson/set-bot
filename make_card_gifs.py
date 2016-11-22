import cairosvg

numbers = ['One', 'Two', 'Three']
colors = ['Red', 'Green', 'Purple']
shadings = ['Solid', 'Shaded', 'Hollow']
shapes = ['Squiggle', 'Oval', 'Diamond']

for number in numbers:
    for color in colors:
        for shading in shadings:
            for shape in shapes:
                card_name = 'Card{}{}{}{}'.format(number, color, shading, shape)
                source_filename = 'cards/{}.svg'.format(card_name)
                target_filename = 'cards/{}Small.svg'.format(card_name)
                with open(source_filename, 'r') as fr:
                    file_contents = fr.read()
                    lines = file_contents.split('\n')
                    svg_tag_index = (i for i, v in enumerate(lines) if '<svg' in v).next()
                    lines[svg_tag_index] = lines[svg_tag_index].replace('"320"', '"160"').replace('"200"', '"100"')
                    lines.insert(svg_tag_index+1, '<g transform="scale(0.5, 0.5)">')
                    lines.insert(len(lines)-2, '</g>')
                    resized = '\n'.join(lines).replace('height="8"', 'height="12"')
                    with open(target_filename, 'w') as fw:
                        fw.write(resized)

                cairosvg.svg2png(
                    url='cards/{}Small.svg'.format(card_name),
                    write_to='cards/{}.png'.format(card_name),
                )
