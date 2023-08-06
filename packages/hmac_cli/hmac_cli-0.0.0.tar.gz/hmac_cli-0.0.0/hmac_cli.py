#!/usr/bin/env python

import hashlib
import hmac

import click


@click.command()
@click.option('--key', prompt=True, hide_input=True,
              confirmation_prompt=True,
              help='encryption key. Will prompt for if not provided.')
@click.option('--algorithm', required=False,
              type=click.Choice(hashlib.algorithms), default='sha1',
              help='algorithm to use')
@click.argument('input_file', type=click.File('rb'))
def cli(key, algorithm, input_file):
    """Encrypt data in INPUT_FILE using HMAC

    with provided secret cryptographic key
    """
    key = key.encode('ascii')
    digestmod = getattr(hashlib, algorithm)
    hmac_obj = hmac.new(key, input_file.read(), digestmod)
    print(hmac_obj.hexdigest())


if __name__ == '__main__':
    cli()
