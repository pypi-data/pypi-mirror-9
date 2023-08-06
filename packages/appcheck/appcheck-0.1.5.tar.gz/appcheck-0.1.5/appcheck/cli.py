# Copyright (c) 2015 Codenomicon Ltd.
# License: MIT

from __future__ import absolute_import, division, print_function

import json
import os.path
from tempfile import NamedTemporaryFile
from zipfile import ZipFile
import click

from appcheck.appcheck import Appcheck
from appcheck.config import AppcheckClientConfig
from appcheck.utils import clean_version, zip_directory
from appcheck import exceptions

import logging

logger = logging.getLogger(__name__)

VERDICT_PASS_SYMBOL = u"\U0001F60A"  # SMILING FACE WITH SMILING EYES
VERDICT_FAIL_SYMBOL = u"\U0001F622"  # CRYING FACE
VERDICT_VERIFY_SYMBOL = u"\U0001f440"  # EYES


def get_appcheck():
    config = AppcheckClientConfig()
    username, password = config.credentials()
    if not (username and password):
        click.echo("Login required.")
        username, password = update_login_credentials()
    # Support alternate Appcheck address, e.g. appliance. None for default.
    appcheck_host = config.get_appcheck_host()
    appcheck = Appcheck(creds=(username, password), host=appcheck_host)
    return appcheck

@click.group(help="Appcheck commandline tools. To use this tool you need "
                  "to have an account to Codenomicon Appcheck service.")
def cli():
    """Appcheck command line utility"""


@cli.add_command
@click.command()
def groups():
    """List groups"""
    appcheck = get_appcheck()
    groups = appcheck.list_groups()
    click.echo('Available groups')
    click.echo('{id:8s} {name}'.format(id='ID', name='Name'))
    for g in groups['groups']:
        click.echo('{id:<8d} {name}'.format(**g))


@cli.add_command
@click.option('--group', help="Show applications in GROUP", metavar="GROUP")
@click.command()
def list(group):
    """List apps"""
    appcheck = get_appcheck()
    apps = appcheck.list_apps(group=group)

    APP_FORMAT = u"{id:5s}  {name}"
    if len(apps['products']) > 0:
        click.echo(APP_FORMAT.format(id="ID", name="Application name"))
        for p in apps['products']:
            click.echo(APP_FORMAT.format(id=str(p['id']),
                                                name=p['name']))
    else:
        click.echo("No apps found.")


@cli.add_command
@click.argument('id_or_sha1', 'Appcheck analysis ID or file SHA1 hash')
@click.option('json_output', '--json/--human', default=False,
              help='Output in machine-readable JSON or human')
@click.command()
def result(id_or_sha1, json_output):
    """Get scan result"""
    appcheck = get_appcheck()
    try:
        data = appcheck.get_result(id_or_sha1=id_or_sha1)
    except exceptions.ResultNotFound:
        click.echo("Result not found")
        return

    if json_output:
        click.echo(json.dumps(data))
        return

    results = data['results']

    summary = results['summary']
    filename = results.get('filename', "")
    sha1 = results.get('sha1sum')
    components = results.get('components', [])
    report_url = results.get('report_url')

    # Component analysis
    component_texts = set()
    for c in components:
        c_lib = c.get('lib')
        c_version = c.get('version')
        if c_version:
            c_version = clean_version(c_version)
            c_text = "{lib} ({version})".format(lib=c_lib, version=c_version)
        else:
            c_text = "{lib}".format(lib=c_lib)
        component_texts.add(c_text)
    # Number of vulnerable components
    vuln_components = sum([1 for c in components if c['vulns']])
    total_components = len(components)

    # License analysis
    lic_unknown = {'name': 'UNKNOWN'}
    licenses = [x.get('license', lic_unknown)['name'] for x in components]

    # Print output
    click.echo("Appcheck analysis results")
    click.echo("    File:   {name}".format(name=filename))
    click.echo("    SHA1:   {sha1}".format(sha1=sha1))
    if report_url:
        click.echo("    Report: {uri}".format(uri=report_url))

    if not results['status'] == Appcheck.STATUS_READY:
        click.echo("Result not yet ready.")
        return

    if component_texts:
        click.echo()
        click.echo('Components:')
        click.echo('    ' + ' '.join(sorted(component_texts)))
    else:
        click.echo("No 3rd party or open source components detected.")

    if licenses:
        click.echo()
        click.echo('License analysis:')
        click.echo('    ' + ' '.join(sorted(set(licenses))))

    click.echo()
    verdict = summary['verdict']['short']
    if verdict == 'Verify':
        symbol = VERDICT_VERIFY_SYMBOL
    elif verdict == 'Vulns':
        symbol = VERDICT_FAIL_SYMBOL
    elif verdict == 'Pass':
        symbol = VERDICT_PASS_SYMBOL
    else:
        symbol = '??'
    click.echo('Vulnerability analysis:')
    click.echo(u'    {vuln} out of {total} components contain known '
                'vulnerabilities {sym}'.format(vuln=vuln_components,
                                               total=total_components,
                                               sym=symbol))
    click.echo(u'    ' + summary['verdict']['detailed'])


@cli.add_command
@click.argument('file', 'file to analyze', nargs=-1, required=True, type=click.Path(exists=True))
@click.option('--group', help="Upload to group id GROUP (see appcheck group)",
              metavar="GROUP", type=int)
@click.command()
def scan(file, group):
    """Analyze a file or directory using Appcheck.

    If a directory is analyzed, it will be compressed to a ZIP archive before
    upload.
    """
    appcheck = get_appcheck()

    progress = True
    file_count = len(file)
    click.echo('Uploading {count} objects...'.format(count=file_count))
    for i, f in enumerate(file):
        display_name = click.format_filename(f)
        click.echo(display_name)
        if os.path.isdir(f):
            # Upload directory as ZIP
            logger.info("Zipping directory...")
            zip_name = "{dirname}.zip".format(
                dirname=os.path.basename(display_name.rstrip(os.path.sep)))
            with NamedTemporaryFile() as tmp_file:
                with ZipFile(tmp_file.name, 'w') as zip_file:
                    zip_directory(f, zip_file)
                result = appcheck.upload_file(tmp_file.name,
                                              display_name=zip_name,
                                              group=group)
        else:
            result = appcheck.upload_file(f, group=group)
        if result['results']['status'] == Appcheck.STATUS_READY:
            status = 'READY; scanned before'
        else:
            status = 'queued for scanning'
        report_url = result['results']['report_url']
        sha1_checksum = result['results']['sha1sum']
        click.echo(" - SHA1: {sha1}".format(sha1=sha1_checksum))
        click.echo(" - {url} ({status})".format(url=report_url,
                                                 status=status))


@cli.add_command
@click.argument('id_or_sha1', 'Appcheck analysis ID or file SHA1 hash')
@click.command()
def delete(id_or_sha1):
    """Delete scan result"""
    appcheck = get_appcheck()

    click.confirm('Really delete all data for result?'.format(id=id_or_sha1), abort=True)
    try:
        appcheck.delete(id_or_sha1)
    except exceptions.ResultNotFound:
        click.echo("Result was not found")
        return


@cli.add_command
@click.command()
def logout():
    """Forget saved username and password"""
    config = AppcheckClientConfig()
    config.forget_credentials()


def update_login_credentials():
    username = click.prompt("Login username/email-address")
    password = click.prompt("Login password", hide_input=True)
    config = AppcheckClientConfig()
    if click.confirm('Save information and do not ask again?'):
        config.set_credentials(username, password)
        click.echo("Saved login details.")
    return username, password


def main(retries=2):
    try:
        for i in range(0, retries):
            try:
                cli(obj={})
            except exceptions.InvalidLoginError:
                click.echo("Login failed. Please log in again.")
                update_login_credentials()
        else:
            click.echo("Out of retries, aborting.")
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
