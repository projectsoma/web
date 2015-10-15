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

social = (Page('https://github.com/projectsoma', 'GitHub', 'github'),
          Page('https://www.youtube.com/channel/UCYGj-PiTrQdITk1zw7kcw7g', 'YouTube', 'youtube-play'))


def ordered_load(stream, Loader=yaml.Loader, object_pairs_hook=collections.OrderedDict):
    class OrderedLoader(Loader):
        pass
    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))
    OrderedLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        construct_mapping)
    return yaml.load(stream, OrderedLoader)


def read_devices(folder):

    d = []

    for f in folder.glob('*.yaml'):

        with f.open('r', encoding='utf-8') as fp:
            dev = ordered_load(fp, yaml.SafeLoader)
            dev['code'] = f.stem

            try:
                with folder.joinpath(dev['build_info']).open('r', encoding='utf-8') as fi:
                    dev['build_info'] = fi.read()
            except KeyError:
                print('No extra build info for %s' % dev['code'])
                dev['build_info'] = ''
            except Exception as e:
                print('Error while loading build info for %s: %s' % (dev['code'], e))
                dev['build_info'] = ''
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
