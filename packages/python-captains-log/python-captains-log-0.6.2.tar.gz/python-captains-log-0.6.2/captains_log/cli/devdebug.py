# -*- coding: utf-8 -*-
import click, peewee

from captains_log.backend.init import init_database
from captains_log.backend.models import CaptainsLogDatabase, Category, Entry

from captains_log.conf import settings

@click.command()
@click.pass_context
def foo_command(ctx):
    """
    To debug some things
    """
    print "LANGUAGE_CODE:", settings.LANGUAGE_CODE
    init_database()
    
    click.echo('Foo')
    print "DATABASE_FILEPATH:", settings.DATABASE_FILEPATH
    print settings.as_json()