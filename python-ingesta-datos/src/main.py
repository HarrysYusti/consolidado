import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

import click
from configuration import setup_logging
from pipelines.cubos.process_cubos import cubos_main
from pipelines.panel_digital.process_panel_digital import panel_digital_main

logger = setup_logging("entrypoint")

MAP_PROCESS = {
    'cubos': cubos_main,
    'panel_digital': panel_digital_main,
}

@click.command()
@click.argument('process_name')
def run(process_name):

    if process_name in MAP_PROCESS.keys():
        logger.info(f"Executing process: `{process_name}`")
        MAP_PROCESS[process_name]()
    else:
        logger.error(f"Executing process `{process_name}` is not implemented")
        print(f"Executing process `{process_name}` is not implemented")

if __name__ == '__main__':
    run()
