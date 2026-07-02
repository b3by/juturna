"""
Serve the Juturna pipeline manager

Set up the Juturna pipeline manager and serve it on a provided host:port pair.
The service is spawned by targeting a running folder for all the created
pipelines, and log level, format, and destination file.

Serving the Juturna manager requires Juturna to be installed with the
`httpwrapper` dependency group.
"""

from juturna.cli import _cli_utils
from juturna.cli.commands._juturna_service import run


def setup_parser(subparsers):  # noqa: D103
    parser = subparsers.add_parser(
        'serve',
        help='launch the Juturna pipeline manager service',
    )

    parser.add_argument(
        '--host',
        '-H',
        required=True,
        type=str,
        help='juturna service host address',
    )

    parser.add_argument(
        '--port',
        '-p',
        required=True,
        type=int,
        help='juturna service port',
    )

    parser.add_argument(
        '--folder',
        '-f',
        required=True,
        type=str,
        help='juturna service pipeline folder',
    )

    parser.add_argument(
        '--log-config',
        '-l',
        type=_cli_utils._is_file_ok,
        help='log configuration file',
    )

    parser.add_argument(
        '--dev',
        '-d',
        action='store_true',
        help='run service in development mode',
    )


def _execute(args):
    run(args.host, args.port, args.folder, args.log_config, args.dev)
