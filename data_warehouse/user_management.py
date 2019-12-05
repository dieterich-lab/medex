import click
from passlib.hash import sha256_crypt

import data_warehouse.redis_rwh as rwh

@click.group()
@click.option('--host', default='127.0.0.1')
@click.option('--port', default='6379')
@click.pass_context
def cli(ctx, host, port):
    ctx.ensure_object(dict)
    ctx.obj['host'] = host
    ctx.obj['port'] = port

@cli.command()
@click.pass_context
@click.argument('username')
def delete_user(ctx, username):
    print('delete user')
    host = ctx.obj.get('host')
    port = ctx.obj.get('port')
    rdb = rwh.get_connection(host, port)
    user_exists = rdb.hexists('users', username)
    if not user_exists:
        click.echo('User "{}" does not exist, so cannot be deleted'.format(username))
        exit(1)
    # else
    rdb.hdel('users', username)
    click.echo('User "{}" successfully deleted'.format(username))
    exit(0)

@cli.command()
@click.pass_context
@click.argument('username')
@click.argument('password')
def create_user(ctx, username, password):
    host = ctx.obj.get('host')
    port = ctx.obj.get('port')
    encrypted_password = sha256_crypt.hash(password)
    rdb = rwh.get_connection(host, port)
    user_exists = rdb.hexists('users', username)
    if user_exists:
        click.echo('User "{}" already exists'.format(username))
        exit(1)
    # hash set = 'users', key1 = username, key2 = 'password', value2 = password
    rdb.hmset('users', {username: encrypted_password})
    click.echo('User "{}" successfully created'.format(username))
    exit(0)

if __name__ == '__main__':
    cli(obj={})

# todo: reset password
# todo: create users from file