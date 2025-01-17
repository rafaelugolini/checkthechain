from __future__ import annotations

from ctc import rpc
from ctc import spec


async def async_get_underlying_asset(
    pool_token: spec.Address,
    provider: spec.ProviderReference = None,
) -> spec.Address:
    function_abi: spec.FunctionABI = {
        'name': 'UNDERLYING_ASSET_ADDRESS',
        'inputs': [],
        'outputs': [{'type': 'address'}],
    }
    result = await rpc.async_eth_call(
        to_address=pool_token,
        function_abi=function_abi,
        provider=provider,
    )
    if not isinstance(result, str):
        raise Exception('invalid rpc result')
    return result
