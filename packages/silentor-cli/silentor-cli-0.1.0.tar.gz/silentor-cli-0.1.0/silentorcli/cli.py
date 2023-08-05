# -*- coding: utf-8 -*-
import click
import os
from silentorcli import __version__
from path import Path


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo(__version__)
    ctx.exit()


@click.group()
@click.option('--version', is_flag=True, callback=print_version,
              expose_value=False, is_eager=True, help='Show the version')
def main():
    """
    Welecome to silentor cli!
    """
    pass

@main.command('new')
@click.argument('name', default='silentor')
def new_silentor(name):
    """
    New a silentor application
    """
    import json
    import os
    import codecs

    __ROOT__ = Path(os.path.dirname(__file__)).parent  # silentor-cli/
    Silentor_Path = os.path.join(__ROOT__, 'silentor')
    # 创建目录
    cwd = os.getcwd()
    os.system('cp -r {_from} {cwd}/{name}'.format(_from=Silentor_Path, cwd=cwd, name=name))
    os.system('rm -rf {cwd}/{name}/.git'.format(cwd=cwd, name=name))

    # 修改配置
    with codecs.open(Silentor_Path+'/default_config.json', encoding='utf-8') as f:
        default_config = json.loads(f.read())

    default_config['app_name'] = name

    with codecs.open('{cwd}/{name}/default_config.json'.format(cwd=cwd, name=name),
                     mode='w', encoding='utf-8') as f:
        f.write(json.dumps(default_config))

    with codecs.open('{cwd}/{name}/config.json'.format(cwd=cwd, name=name),
                     mode='w', encoding='utf-8') as f:
        f.write(json.dumps(default_config))

    click.echo('Well done! Run you application with follow command:')
    click.echo('cd %s && silentor server' % name)


@main.command('upgrade')
@click.argument('version', default='latest')
def upgrade_silentor():
    """
    Upgrade silentorcli version [NOT FInish YET!]
    """
    pass


@main.command('version')
def version():
    """
    Get the latest version infomation
    """
    click.echo('Fetching........Please wait')
    from github import GitHub
    rc = GitHub().get_silentor_latest()
    click.echo('verison: %s' % rc['tag_name'])
    click.echo('Note:\r\n%s' % rc['body'])


@main.command('server')
@click.argument('port', default=8000)
def server(port):
    """
    Server your silentor application
    """
    click.echo('======== Tips ==============')
    click.echo('=== press Ctrl+C to stop ===')
    click.echo('============================')

    cmds = [
        'cd %s' % os.getcwd(),
        'cd ..',
        'python -m SimpleHTTPServer %s' % port,
        'cd %s' % os.getcwd(),
    ]
    name = os.path.split(os.getcwd())[1]
    click.launch('http://localhost:{port}/{name}/index.html'.format(port=port,name=name) )
    os.system(' && '.join(cmds))
