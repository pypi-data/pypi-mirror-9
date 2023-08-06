# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals


import sys
import json
import click
import hashlib
import pyscrypt
import base58
import libnacl.public
import libnacl.secret

XID_PREFIX = b'\xea'


def generate_keypair(sk=None):
    """
    Generate a random key pair.
    :return:
    """
    if sk:
        keypair = libnacl.public.SecretKey(sk=sk)
    else:
        keypair = libnacl.public.SecretKey()

    return keypair.pk, keypair.sk


def key_to_xid(key):
    """
    Generate an address from a public key.
    :param key: the 32-byte byte string.
    :return:
    """
    sha256 = hashlib.sha256()
    sha256.update(XID_PREFIX)
    sha256.update(key)
    sum = sha256.digest()
    addr = XID_PREFIX + key + sum[:2]

    return base58.b58encode(addr)


def validate_xid(addr):
    """
    Check if the provided address is valid or not.

    :param addr: address in base58 string.
    :return:
    """
    val = base58.b58decode(addr)
    #assert len(val) == 35

    if len(val) != 35:
        return False

    prefix = val[0]
    if prefix != XID_PREFIX:
        return False

    sha256 = hashlib.sha256()
    sha256.update(XID_PREFIX)
    sha256.update(val[1:33])
    sum = sha256.digest()

    if val[-2:] != sum[:2]:
        return False

    return True


def derive_secret_key(password, salt):
    if isinstance(password, unicode):
        password = password.encode('utf-8')
    if isinstance(salt, unicode):
        salt = salt.encode('utf-8')

    sk = pyscrypt.hash(password=password,
                       salt=salt,
                       N=1024,
                       r=1,
                       p=1,
                       dkLen=32)
    return sk


def gen_random_key(ctx):
    if ctx.obj['verbose']:
        click.echo("Generating random key...")
    (pk, sk) = generate_keypair()
    xid = key_to_xid(pk)
    res = dict(xid=xid, key=base58.b58encode(pk), secret=base58.b58encode(sk))
    click.echo(json.dumps(res, sort_keys=True, indent=4, separators=(',', ': ')))
    return 0


@click.group()
@click.option('--verbose', '-v', is_flag=True,
              help='Enables verbose mode.')
@click.pass_context
def cli(ctx, verbose):
    ctx.obj = dict(verbose=verbose)


@cli.command()
@click.option('--salt', '-s',
              help='Value for increasing randomness, e.g. email address.')
@click.option('--password', '-p',
              help='Hard to guess password.')
@click.pass_context
def generate(ctx, salt, password):
    if not salt and not password:
        return gen_random_key(ctx)

    if not (salt and password):
        if not salt:
            click.echo("Missing option: salt")
        if not password:
            click.echo("Missing option: password")
        return 1

    sk = derive_secret_key(password, salt)
    (pk, sk) = generate_keypair(sk=sk)
    xid = key_to_xid(pk)
    res = dict(xid=xid, key=base58.b58encode(pk), secret=base58.b58encode(sk))
    click.echo(json.dumps(res, sort_keys=True, indent=4, separators=(',', ': ')))
    return 0


@cli.command()
@click.option('--xid', '-i',
              help='Exchange ID')
@click.option('--key', '-k',
              help='Public key')
@click.option('--secret', '-s',
              help='Secret key')
@click.pass_context
def validate(ctx, xid, key, secret):
    if xid:
        if validate_xid(xid):
            click.echo("XID %s is valid." % xid)
        else:
            click.echo("XID %s is invalid." % xid)

    if key and secret:
        sk = base58.b58decode(secret)
        pk = base58.b58decode(key)
        (vpk, vsk) = generate_keypair(sk=sk)
        if vpk == pk and vsk == sk:
            click.echo("Key and secret are valid and matched.")
            return 0
        click.echo("Key or secret is invalid or mismatched.")
        return 1

    if key or secret:
        click.echo("Options key and secret should be given together.")
        return 1

if __name__ == '__main__':
    sys.exit(cli())