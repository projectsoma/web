from io import open
import os
import pathlib
import collections

from jinja2 import FileSystemLoader
from jinja2.environment import Environment
import yaml

Page = collections.namedtuple('Page', 'url title icon')

pages = (Page('index', 'HOME', None), Page('about', 'QUIENES SOMOS', None),
         Page('devices', 'DISPOSITIVOS', None))

social = (Page('https://github.com/projectsoma', 'GitHub', 'github'), )


def read_devices(folder):

    d = []

    for f in folder.glob('*.yaml'):

        with f.open('r', encoding='utf-8') as fp:
            dev = yaml.load(fp)
            dev['code'] = f.stem
            d.append((f.stem, dev))

    return collections.OrderedDict(sorted(d))


def main(tmpl_folder, output_folder, devices):

    env = Environment(loader=FileSystemLoader(str(tmpl_folder)))

    persons = []

    for page in pages:

        print('Processing: %s' % page.title)

        main = env.get_template(page.url + '.html')

        with output_folder.joinpath(
            page.url + '.html').open(mode='w',
                                     encoding='utf-8') as fp:
            fp.write(main.render(pages=pages,
                                 active=page.url,
                                 social=social,
                                 devices=devices))

    main = env.get_template('device.html')

    for key, device in devices.items():

        print('Processing device %s' % key)

        with output_folder.joinpath('d', key + '.html').open(
            mode='w',
            encoding='utf-8') as fp:
            fp.write(main.render(pages=pages,
                                 active=None,
                                 social=social,
                                 rel_root='../',
                                 **device))

    print('\nDone -> %s' % output_folder.joinpath('index.html'))

if __name__ == '__main__':
    root = pathlib.Path('.')
    main(root.joinpath('templates', 'es'), root.joinpath('site'),
         read_devices(root.joinpath('devices', 'es')))
