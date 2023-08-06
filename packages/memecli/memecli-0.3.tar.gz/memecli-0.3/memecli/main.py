import click
import memeapi as meme
import yaml
from os.path import expanduser
from tabulate import tabulate


_headers = ['displayName', 'urlName', 'generatorID', 'imageUrl',
            'instancesCount', 'ranking', 'totalVotesScore']

_meme_headers = [
    'displayName', 'urlName', 'text0', 'text1', 'instanceImageUrl',
    'generatorID', 'imageUrl', 'totalVotesScore', 'instanceID', 'instanceUrl',
]


def _format_for_tabulate(headers, data, keys=None):
    formatted_data = []
    if keys is None:
        keys = headers
    for d in data:
        row = []
        for key in keys:
            row.append(d[key])
        formatted_data.append(row)
    formatted_data.insert(0, headers)
    return formatted_data


def _print_table(headers, data, keys=None):
    output_data = _format_for_tabulate(headers, data, keys)
    output = tabulate(output_data, headers='firstrow')
    click.echo(output)


def _get_config():
    """Parse and retrieve configuration file."""
    with open(expanduser('~/.memecli.yml'), 'r') as f:
        raw_config = f.read()
    config = yaml.load(raw_config)
    return config


@click.group()
@click.version_option()
def cli():
    """Command line wrapper over http://memegenerator.net API"""
    pass


@click.command('new')
@click.argument('meme-alias')
@click.argument('top-text')
@click.argument('bottom-text')
def new(meme_alias, top_text, bottom_text):
    """
    Convenient way of create a new meme instance.
    To work, need a .memecli.yml file in the user home directory, with a
    username, password, and a list of meme aliases.
    """
    config = _get_config()
    response = meme.instances_create(
        config['username'],
        config['password'],
        config['memes'][meme_alias]['generator'],
        config['memes'][meme_alias]['image'],
        top_text,
        bottom_text,
        config['language_code']
    )

    if response['success']:
        click.echo(response['result']['instanceImageUrl'])


@click.command('list')
def list_():
    """
    Lists meme aliases
    """
    config = _get_config()
    for meme in sorted(config['memes'].keys()):
        click.echo(meme)


@click.command('template-search')
@click.option('-q', '--q', required=True, prompt='Q (search term)')
@click.option('-i', '--page-index', type=int)
@click.option('-s', '--page-size', type=int)
def generators_search(q, page_index, page_size):
    """Returns a list of search results filtered by search term."""
    response = meme.generators_search(q=q, page_index=page_index,
                                      page_size=page_size)
    if response['success']:
        _print_table(_headers, response['result'])


@click.command('template-select-by-popular')
@click.option('-i', '--page-index', type=int)
@click.option('-s', '--page-size', type=int)
@click.option('-d', '--days', type=int)
def generators_select_by_popular(page_index, page_size, days):
    """Returns the most popular generators for the last n days."""
    response = meme.generators_select_by_popular(
        page_index=page_index, page_size=page_size, days=days
    )

    if response['success']:
        _print_table(_headers, response['result'])


@click.command('template-select-by-new')
@click.option('-i', '--page-index', type=int)
@click.option('-s', '--page-size', type=int)
def generators_select_by_new(page_index, page_size):
    """Returns the most recently created generators."""
    response = meme.generators_select_by_new(page_index=page_index,
                                             page_size=page_size)

    if response['success']:
        _print_table(_headers, response['result'])


@click.command('template-select-by-trending')
def generators_select_by_trending():
    """Returns recently trending generators."""
    response = meme.generators_select_by_trending()
    if response['success']:
        _print_table(_headers, response['result'])


@click.command('template-select-related-by-name')
@click.option('-n', '--display-name', required=True, prompt='Display name')
def generators_select_related_by_display_name(display_name):
    """
    Returns generators that are related to a particular generator, a sort of
    'see also' list.
    """
    response = meme.generators_select_related_by_display_name(
        display_name=display_name
    )
    if response['success']:
        headers = ['displayName', 'urlName', 'imageUrl', 'instancesCount']
        _print_table(headers, response['result'])


@click.command('template-select-by-url-name-or-generator-id')
@click.option('-u', '--url-name', required=True, prompt='URL name')
@click.option('-g', '--generator-id', type=int)
def generators_select_by_url_name_or_generator_id(url_name, generator_id):
    """
    Returns information about a specific generator, either by its generator_id
    or by its url_name.
    """
    response = meme.generators_select_by_url_name_or_generator_id(
        url_name=url_name, generator_id=generator_id
    )
    if response['success']:
        headers = _headers
        headers.extend(('templatesCount', 'description',))
        _print_table(headers, [response['result']])


@click.command('meme-select-by-popular')
@click.option('-i', '--page-index', type=int)
@click.option('-s', '--page-size', type=int)
@click.option('-u', '--url-name')
@click.option('-d', '--days', type=int)
@click.option('-l', '--language-code', default='en')
def instances_select_by_popular(page_index, page_size, url_name, days,
                                language_code):
    """Returns the most popular instances for a particular criteria."""
    response = meme.instances_select_by_popular(
        page_index=page_index, page_size=page_size, url_name=url_name,
        days=days
    )
    if response['success']:
        _print_table(_meme_headers, response['result'])


@click.command('meme-create')
@click.option('-u', '--username', required=True, prompt='Username')
@click.option('-p', '--password', required=True, prompt='Password')
@click.option('-g', '--generator-id', type=int, required=True, prompt='Generator ID')
@click.option('-i', '--image-id', type=int, required=True, prompt='Image ID')
@click.option('-t', '--top-text', required=True, prompt='Top text')
@click.option('-b', '--bottom-text', required=True, prompt='Bottom text')
@click.option('-l', '--language-code', default='en')
def instances_create(username, password, generator_id, image_id, top_text,
                     bottom_text, language_code):
    """Creates a captioned image."""
    response = meme.instances_create(
        username=username, password=password, generator_id=generator_id,
        image_id=image_id, text_0=top_text, text_1=bottom_text,
        language_code=language_code
    )
    click.echo(response)


@click.command('meme-select-by-new')
@click.option('-i', '--page-index', type=int)
@click.option('-s', '--page-size', type=int)
@click.option('-u', '--url-name')
@click.option('-l', '--language-code', default='en')
def instances_select_by_new(page_index, page_size, url_name, language_code):
    """Returns recently created instances, for a particular criteria."""
    response = meme.instances_select_by_new(
        page_index=page_index, page_size=page_size, url_name=url_name,
        language_code=language_code
    )
    if response['success']:
        _print_table(_meme_headers, response['result'])


@click.command('meme-select')
@click.option('-i', '--instance-id', type=int, required=True, prompt='Instance ID')
def instances_select(instance_id):
    """ Select an instance by its instance id."""
    response = meme.instances_select(instance_id=instance_id)
    click.echo(response)


@click.command('content-flag-create')
@click.option('-u', '--content-url', required=True, prompt='Content URL')
@click.option('-r', '--reason', required=True, prompt='Reason')
@click.option('-e', '--email', required=True, prompt='Email')
def content_flag_create(content_url, reason, email):
    """ Flag content for removal, for cases of harassment etc."""
    response = meme.content_flag_create(content_url=content_url, reason=reason,
                                        email=email)
    click.echo(response)


cli.add_command(new)
cli.add_command(list_)
cli.add_command(generators_search)
cli.add_command(generators_select_by_popular)
cli.add_command(generators_select_by_new)
cli.add_command(generators_select_by_trending)
cli.add_command(generators_select_related_by_display_name)
cli.add_command(generators_select_by_url_name_or_generator_id)
cli.add_command(instances_select_by_popular)
cli.add_command(instances_create)
cli.add_command(instances_select_by_new)
cli.add_command(instances_select)
cli.add_command(content_flag_create)


if __name__ == '__main__':
    cli()
