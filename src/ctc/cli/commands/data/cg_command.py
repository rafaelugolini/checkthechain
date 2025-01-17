from __future__ import annotations

import toolcli

from ctc.protocols import coingecko_utils


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_cg_command,
        'help': 'output coingecko market data',
        'args': [
            {'name': '-n', 'help': 'number of entries to include in output'},
            {
                'name': '--verbose',
                'action': 'store_const',
                'const': True,
                'default': None,
                'help': 'include extra data',
            },
            {'name': '--height', 'help': 'height, number of rows per asset'},
            {'name': '--width', 'help': 'width of sparklines'},
        ],
        'examples': [
            '',
            '-n 100',
        ],
    }


async def async_cg_command(
    *,
    n: int,
    verbose: bool,
    height: int | None,
    width: str | int | None,
) -> None:
    if height is None:
        height = 1
    height = int(height)

    if isinstance(width, str):
        width = int(width)

    if n is None:
        n = toolcli.get_n_terminal_rows() - 3
        n = int(n / height)
    else:
        n = int(n)

    data = await coingecko_utils.async_get_market_data(n)

    if verbose is None:
        verbose = toolcli.get_n_terminal_cols() >= 96

    coingecko_utils.print_market_data(
        data=data,
        verbose=verbose,
        height=height,
        width=width,
    )
