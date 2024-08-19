import click
import pytest
from plumbum import local
from copy import deepcopy
from device import SupportedDevices
from station import SupportedStations
import os

OPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEST_DIR = os.path.join(OPT_DIR, "tests")

def _construct_help_msg():
    msg = """
    Usage,
    \b
    run-qual --device-type ABC --qual-station XYZ --dut 1234
    \b
    """


def _validate_device_station_map(station: dict, device: dict) -> None:
    """
    Helper to validate the product types supported in the given test station.
    :param station: Station details in dict
    :param device: Product types supported by the framework
    :return:
    """
    supported_devices = SupportedStations.supported_stations().get(station).get('devices')
    if device not in supported_devices:
        # TODO: logging
        raise Exception(f'Device {device} is not supported in station {station}')
    return None


def invoke_pytest(args, plugins=None):
    """
    Invokes pytest.main with arguments and plugins if any provided.
    :param args:
    :param plugins:
    :return:
    """
    try:
        # TODO: Below hardcoded path has to be replaced.
        #with local.cwd("/Users/kathir/mydev/optiqual/tests"):
        with local.cwd(TEST_DIR):
            args = [str(arg) for arg in args]
            return_code = pytest.main(args, plugins=plugins)
    except Exception:
        # TODO: log and gracefully exit
        raise


@click.group(chain=True)
@click.pass_context
def cli(context):
    """
    Cli entry point, base version which can be extended based
    on the use case/requirements

    :param context: Click context
    :return:
    """
    pass


@cli.command('optiqual', context_settings=dict(ignore_unknown_options=True),
             help=_construct_help_msg())
@click.option("--product-type", type=click.Choice(SupportedDevices.supported_devices()),
              default="10G_LR", help="Use the supported device to run the qual, ex `10G_LR`")
@click.option("--qual-station", type=click.Choice(SupportedStations.supported_stations()),
              default="optiqual1", help="Use the supported test stations , ex `STATION1`")
@click.option("--dut", type=click.STRING, default="MINDSERV",
              help="Provide DUT's serial number if needed")
@click.argument('pytest_args', nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def run_optiqual(context, product_type, qual_station, dut, pytest_args):
    if '--help' in pytest_args:
        click.echo(_construct_help_msg())
    _validate_device_station_map(qual_station, product_type)
    args = ['--product-type', product_type, '--qual-station', qual_station, '--dut', dut]
    args += ['-v', '-s'] + list(pytest_args)
    invoke_pytest(args=deepcopy(args))


if __name__ == '__main__':
    cli()
