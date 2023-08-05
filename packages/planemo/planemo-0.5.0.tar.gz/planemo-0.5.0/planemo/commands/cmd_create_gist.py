"""
"""
import click

from planemo.cli import pass_context
from planemo.io import info
from planemo import github_util

target_path = click.Path(
    file_okay=True,
    dir_okay=False,
    resolve_path=True,
)


@click.command("create_gist")
@click.argument(
    'path',
    metavar="FILE_PATH",
    type=target_path,
)
@click.option(
    "--link_type",
    type=click.Choice(["raw", "html"]),
    default="raw",
    help=("Link type to generate for the file.")
)
@pass_context
def cli(ctx, path, **kwds):
    """Download a tool repository as a tarball from the tool shed and extract
    to the specified directory.
    """
    file_url = github_util.publish_as_gist_file(ctx, path)
    if kwds.get("link_type") == "raw":
        share_url = file_url
    else:
        share_url = "http://htmlpreview.github.io/?%s" % file_url
    info("File published to Github Gist - share with %s" % share_url)
