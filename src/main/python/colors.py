import yaml


class Colors:

    def __init__(self, color_names_file='colors.yaml'):
        with open(color_names_file) as f:
            yaml_data = yaml.safe_load(f)

        self.colors_by_name = {}
        for color in yaml_data['colors']:
            color_name_normalized = str(color['name']).lower().replace(' ', '')
            self.colors_by_name[color_name_normalized] = color['code']

    def html_color_to_rgb(self, color_string):
        rrggbb_string = self.get_color_by_name(color_string)

        """ convert #RRGGBB to an (R, G, B) tuple """
        rrggbb_string = rrggbb_string.strip()
        if rrggbb_string[0] == '#': rrggbb_string = rrggbb_string[1:]
        if len(rrggbb_string) != 6:
            raise ValueError("input #%s is not in #RRGGBB format" % color_string)
        r, g, b = rrggbb_string[:2], rrggbb_string[2:4], rrggbb_string[4:]
        r, g, b = [int(n, 16) for n in (r, g, b)]
        return r, g, b

    def get_color_by_name(self, color_string):
        new_color_string = color_string
        color_string_normalized = str(color_string).lower().replace(' ', '')
        if color_string_normalized in self.colors_by_name:
            new_color_string = self.colors_by_name[color_string_normalized]
        return new_color_string


if __name__ == '__main__':
    colors = Colors()
    color_string = '#ff00cc'
    rgb = colors.html_color_to_rgb(color_string)
    print(color_string, flush=True)
    print(rgb, flush=True)

    color_string = 'Purple Jam'
    rgb = colors.html_color_to_rgb(color_string)
    print(color_string, flush=True)
    print(rgb, flush=True)
    color_string = 'Chicken Yellow'
    rgb = colors.html_color_to_rgb(color_string)
    print(color_string, flush=True)
    print(rgb, flush=True)

