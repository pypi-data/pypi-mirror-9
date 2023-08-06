#!/usr/bin/python
import click
import salt.config
import salt.client


def salt_init():
    opts = salt.config.apply_minion_config()
    opts['file_client'] = 'local'
    caller = salt.client.Caller(mopts=opts)
    return caller


@click.command()
@click.option('-i', '--install',
              help='Install new relic system monitor',
              is_flag=True)
@click.option('-k', '--key', help='new relic data access key', default=False)
def main(install, key):
    """help page"""
    if not install:
        click.echo('Try new_relic --help for useful information!')
    else:
        if not key:
            key = click.prompt('NewRelic data access key')
        caller = salt_init()
        info = dict(
            newrelic_url='http://download.newrelic.com/pub/newrelic/el5/i386/newrelic-repo-5-3.noarch.rpm',
            newrelic_package='newrelic-sysmond',
            newrelic_license_cmd=r"nrsysmond-config --set license_key='%(l_key)s'"
            % {'l_key': key},
            newrelic_start_cmd=r"/etc/init.d/newrelic-sysmond start")
        click.echo(caller.sminion.functions['pkg.install'](sources=[
            {'repo': info['newrelic_url']}
        ]))
        click.echo(caller.sminion.functions['pkg.install'](
            info['newrelic_package'],
            require=[{'pkg': info['newrelic_url']}]))
        click.echo(
            caller.sminion.functions['cmd.run'](info['newrelic_license_cmd']))
        click.echo(
            caller.sminion.functions['cmd.run'](info['newrelic_start_cmd']))


if __name__ == "__main__":
    main()
