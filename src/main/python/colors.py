import re

import yaml

INVALID_COLOR_STRING = "Input '{value}' is not in #RRGGBB format and is not a recognized color name"


class Colors:

    def __init__(self, color_names_file='colors.yaml'):
        with open(color_names_file) as f:
            yaml_data = yaml.safe_load(f)

        self.colors_by_name = {}
        for color in yaml_data['colors']:
            color_name_normalized = self.normalize_color_name(color['name'])
            if color_name_normalized in self.colors_by_name:
                if self.colors_by_name[color_name_normalized] != color['code']:
                    pass
                else:
                    code1 = self.colors_by_name[color_name_normalized]
                    code2 = color['code']
                    print("Duplicate color definitions for {name}: {code1}, {code2}.".format(name=color['name'],
                                                                                             code1=code1,
                                                                                             code2=code2))
                    print("Using first definition, {name}: {code1}.".format(name=color['name'], code1=code1))
            else:
                self.colors_by_name[color_name_normalized] = color['code']

    def normalize_color_name(self, color_name):
        color_name_normalized = str(color_name).lower()
        color_name_normalized = re.sub('[ _]', '', color_name_normalized)
        return color_name_normalized

    def html_color_to_rgb(self, color_string):
        rrggbb_string = self.get_color_by_name(color_string)

        """ convert #RRGGBB to an (R, G, B) tuple """
        rrggbb_string = rrggbb_string.strip()
        if rrggbb_string[0] == '#': rrggbb_string = rrggbb_string[1:]
        if len(rrggbb_string) != 6:
            raise ValueError(INVALID_COLOR_STRING.format(value=color_string))
        r, g, b = rrggbb_string[:2], rrggbb_string[2:4], rrggbb_string[4:]
        try:
            r, g, b = [int(n, 16) for n in (r, g, b)]
        except ValueError:
            raise ValueError(INVALID_COLOR_STRING.format(value=color_string))

        return r, g, b

    def get_color_by_name(self, color_string):
        new_color_string = color_string
        color_string_normalized = str(color_string).lower().replace(' ', '')
        if color_string_normalized in self.colors_by_name:
            new_color_string = self.colors_by_name[color_string_normalized]
        return new_color_string


if __name__ == '__main__':
    colors = Colors('../../../etc/colors.yaml')
    test_color_string = '#ff00cc'
    rgb = colors.html_color_to_rgb(test_color_string)
    print(test_color_string, flush=True)
    print(rgb, flush=True)

    test_color_string = 'Purple Jam'
    rgb = colors.html_color_to_rgb(test_color_string)
    print(test_color_string, flush=True)
    print(rgb, flush=True)
    test_color_string = 'Chicken Yellow'
    rgb = colors.html_color_to_rgb(test_color_string)
    print(test_color_string, flush=True)
    print(rgb, flush=True)
