import binascii

from botocore.utils import calculate_tree_hash
import click

__version__ = '0.2'

@click.command()
@click.option('--output', type=click.Choice(['ascii', 'binary']),
              default='ascii', help='output format of Merkle Tree')
@click.argument('filename', type=click.File('rb'))
def cli(filename, output):
    """calculate Merkle Tree
    """
    hash_value = calculate_tree_hash(filename)
    if output == 'binary':
        hash_value = binascii.unhexlify(hash_value)
    click.echo(hash_value)
