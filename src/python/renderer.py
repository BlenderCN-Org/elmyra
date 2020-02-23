'''
Opens, renders and exports all visualizations in a constant cycle

Optional arguments:
device -- the device to render on - 'CPU' or 'GPU' (default 'CPU')
target_time -- the minimum time to render, in seconds (default 60)
'''


import json
import sys

from argparse import ArgumentParser
from glob import glob
from natsort import natsorted
from os import chdir, path
from time import sleep


# Make this script's directory the current working directory (could be anything else)
# and add it to sys.path (this script runs from blender context)
elmyra_root = path.dirname(path.realpath(__file__))
chdir(elmyra_root)
sys.path.append(elmyra_root)

from lib import common, export, meta, render, version


def parse_custom_args():
    parser = ArgumentParser(prog='Elmyra Renderer Params')
    parser.add_argument('--data-dir', required=True)
    parser.add_argument('--device', default='CPU')
    parser.add_argument('--target-time', type=int, default=60)

    custom_args = sys.argv[sys.argv.index('--') + 1:]

    return parser.parse_args(custom_args)


def find_unrendered(visualizations_dir):
    visualizations_glob = path.join(visualizations_dir, '*')

    for visualization_dir in glob(visualizations_glob):
        latest_version_dir = version.latest_version_dir(visualization_dir)
        meta_dict = meta.read(latest_version_dir)

        if not 'lastRender' in meta_dict:
            return visualization_dir

    return None

def render_visualization(visualization_dir, target_time, device):
    if version.open_latest(visualization_dir):
        render.render(target_time, device)
        export.export()


def render_visualizations(visualizations_dir, target_time, device):
    visualizations_glob = path.join(visualizations_dir, '*')

    for visualization_dir in glob(visualizations_glob):

        # Before regularly rendering the next visualization this
        # loop determines if there is another visualization with a higher
        # priority (= not yet rendered) and renders that first
        while True:
            unrendered_visualization_dir = find_unrendered(visualizations_dir)

            if unrendered_visualization_dir:
                render_visualization(unrendered_visualization_dir, target_time, device)
            else:
                break

        render_visualization(visualization_dir, target_time, device)




args = parse_custom_args()
common.ensure_addons()

visualizations_dir = path.join(args.data_dir, 'visualizations')

while True:
    render_visualizations(visualizations_dir, args.target_time, args.device)
    sleep(1)