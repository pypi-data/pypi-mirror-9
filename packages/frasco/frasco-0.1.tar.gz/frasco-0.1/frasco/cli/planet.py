import click


PLANET_URL = "http://planet.getfrasco.com"


def query_repo(repo_url, action, **params):
    r = requests.get(repo_url + "/" + action, params=params)
    return r.json()


@click.group('planet')
@click.option('--repo', default=PLANET_URL)
@click.pass_context
def planet_command(ctx, repo):
    ctx.obj['repo'] = repo


@planet_command.command()
@click.argument('term')
@click.pass_context
def search(ctx, term):
    click.echo("Searching for '%s'..." % term)


@planet_command.command()
@click.argument('name')
@click.pass_context
def install(ctx, name):
    click.echo("Installing '%s'..." % name)