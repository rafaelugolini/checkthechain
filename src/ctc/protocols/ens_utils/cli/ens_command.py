from __future__ import annotations

import asyncio

import toolcli
import toolstr
import tooltime
from typing_extensions import TypedDict

from ctc import binary
from ctc import evm
from ctc import spec

from ctc.protocols import ens_utils


class ENSResult(TypedDict):
    address: spec.Address | None
    name: str | None
    owner: str | None
    expiration: int | None
    resolver: str | None


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_ens_command,
        'help': 'summarize ENS entry',
        'args': [
            {
                'name': 'name_or_address',
                'nargs': '+',
                'help': 'ENS name(s) or address(es)',
            },
            {'name': '--block', 'help': 'block number'},
            {
                'name': '--verbose',
                'help': 'display additional information',
                'action': 'store_true',
            },
        ],
        'examples': [
            '0xd8da6bf26964af9d7eed9e03e53415d37aa96045',
            'vitalik.eth',
            'vitalik.eth --verbose',
        ],
    }


async def async_ens_command(
    *,
    name_or_address: str,
    block: spec.BlockNumberReference,
    verbose: bool,
) -> None:

    if block is not None:
        block = binary.standardize_block_number(block)

    coroutines = [
        async_process_ens_arg(arg=arg, block=block) for arg in name_or_address
    ]
    results = await asyncio.gather(*coroutines)

    for r, result in enumerate(results):

        if r > 0:
            print()

        if result['name'] is None:
            toolstr.print_text_box(result['address'])
            print('[no ENS records]')
            continue
        elif result['address'] is None:
            toolstr.print_text_box(result['name'])
            print('[no ENS records]')
            continue

        toolstr.print_text_box(result['name'])
        print('- address:', result['address'])
        print('- owner:', result['owner'])
        print('- resolver:', result['resolver'])
        print('- namehash:', ens_utils.hash_name(result['name']))
        # print('- registered:', )
        print(
            '- expiration:',
            tooltime.timestamp_to_iso(result['expiration']).replace('T', ' '),
        )

        if verbose:
            text_records = await ens_utils.async_get_text_records(
                name=result['name']
            )
            if len(text_records) > 0:
                print()
                print()
                toolstr.print_header('Text Records')
                for key, value in sorted(text_records.items()):
                    print('-', key + ':', value)
            else:
                print('- no text records')


async def async_process_ens_arg(
    arg: str, block: spec.BlockNumberReference
) -> ENSResult:

    if '.' in arg:
        name = arg
        address = None
        address_coroutine = ens_utils.async_resolve_name(name, block=block)
    elif evm.is_address_str(arg):
        address = arg
        name = await ens_utils.async_reverse_lookup(address, block=block)
    else:
        raise Exception('could not parse inputs')

    if name == '':
        return {
            'address': address,
            'name': None,
            'owner': None,
            'expiration': None,
            'resolver': None,
        }

    owner_coroutine = ens_utils.async_get_owner(name=name)
    expiration_coroutine = ens_utils.async_get_expiration(name=name)
    resolver_coroutine = ens_utils.async_get_resolver(name=name)

    owner, expiration, resolver = await asyncio.gather(
        owner_coroutine,
        expiration_coroutine,
        resolver_coroutine,
    )

    if address is None:
        address = await address_coroutine

    return {
        'address': address,
        'name': name,
        'owner': owner,
        'expiration': expiration,
        'resolver': resolver,
    }
