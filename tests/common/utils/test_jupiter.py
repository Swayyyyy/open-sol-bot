import pytest
from common.utils.jupiter import JupiterAPI


@pytest.mark.asyncio
async def test_get_quote():
    jupiter_api = JupiterAPI()
    quote = await jupiter_api.get_quote(
        input_mint="So11111111111111111111111111111111111111112",
        output_mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
        amount=100,
        slippage_bps=100,
    )
    # {
    #     "inputMint": "So11111111111111111111111111111111111111112",
    #     "inAmount": "100",
    #     "outputMint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
    #     "outAmount": "66",
    #     "otherAmountThreshold": "66",
    #     "swapMode": "ExactIn",
    #     "slippageBps": 100,
    #     "platformFee": None,
    #     "priceImpactPct": "0",
    #     "routePlan": [
    #         {
    #             "swapInfo": {
    #                 "ammKey": "BQR6JJFyMWxnUERqbCRCCy1ietW2yq8RTKDx9odzruha",
    #                 "label": "Stabble Weighted Swap",
    #                 "inputMint": "So11111111111111111111111111111111111111112",
    #                 "outputMint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
    #                 "inAmount": "100",
    #                 "outAmount": "66",
    #                 "feeAmount": "0",
    #                 "feeMint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
    #             },
    #             "percent": 100,
    #         }
    #     ],
    #     "scoreReport": None,
    #     "contextSlot": 322287008,
    #     "timeTaken": 0.000851243,
    #     "swapUsdValue": "0.0000171469275295053183424833",
    #     "simplerRouteUsed": False,
    # }
    assert quote["inAmount"] == "100"


@pytest.mark.asyncio
async def test_get_swap_transaction():
    jupiter_api = JupiterAPI()
    swap_tx_resp = await jupiter_api.get_swap_transaction(
        input_mint="So11111111111111111111111111111111111111112",
        output_mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
        amount=100,
        user_publickey="J5hkNQTVi18NCEMSGBsMY9mdtHfb5JFpUc4bHE7D89ft",
        slippage_bps=100,
    )
    # {
    #     "swapTransaction": "AQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACAAQAHCv3LExkxfByqoOlsKBdCufSiFrdHvdBtMcv6+jbbk6THAhKj2Dpv5ABJQ3N6fhgccAiAem3gvOKhIHYzZO8lg24/MZgHRxLwGa0Iriw60r7zbZoDjoo3x1dh0cqo9PsrUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAwZGb+UhFzL/7K26csOb57yM5bvF9xJrLEObOkAAAAAEedVb8jHAbu50xW7OaBUH/bGy3qP0jlECsc2iVrwTjwbd9uHXZaGT2cvhRs7reawctIXtX1s3kTqM9YV+/wCpjJclj04kifG7PRApFI4NgwtaE5na/xCEBI572Nvp+Fm0P/on9df2SnTAmx8pWHneSwmrNt/J3VFLMhqns4zl6Mb6evO+2606PWXzaqvJdDGxu+TC0vbg5HymAgNFL11hmLx5Ib3VF7sKwi39qKCrbDGB6WLr2zLgKRLq/SvMfD8IBAAFAjHfBgAEAAkDfuEBAAAAAAAHBgACAA4DBgEBAwIAAgwCAAAAZAAAAAAAAAAGAQIBEQcGAAEACQMGAQEFFgYAAgEFCQUIBQ8AAgENCgsMExESEAYj5RfLl3rjrSoBAAAAOWQAAWQAAAAAAAAAPAAAAAAAAAA5AAAGAwIAAAEJAdnFGG9MSdeb7p9QpGiGlKq6ElUs2KMptC7+ORciTUKYBA4LDQ8GCBUSEQwT",
    #     "lastValidBlockHeight": 301043236,
    #     "prioritizationFeeLamports": 55511,
    #     "computeUnitLimit": 450353,
    #     "prioritizationType": {
    #         "computeBudget": {"microLamports": 123262, "estimatedMicroLamports": 123262}
    #     },
    #     "simulationSlot": 322775328,
    #     "dynamicSlippageReport": {
    #         "slippageBps": 57,
    #         "otherAmount": 60,
    #         "simulatedIncurredSlippageBps": 0,
    #         "amplificationRatio": None,
    #         "categoryName": "solana",
    #         "heuristicMaxSlippageBps": 100,
    #         "rtseSlippageBps": 57,
    #     },
    #     "simulationError": None,
    #     "addressesByLookupTableAddress": None,
    # }
    assert "swapTransaction" in swap_tx_resp


@pytest.mark.asyncio
async def test_get_swap_transaction_use_jito_tip_lamports():
    jupiter_api = JupiterAPI()
    swap_tx_resp = await jupiter_api.get_swap_transaction(
        input_mint="So11111111111111111111111111111111111111112",
        output_mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
        amount=100,
        user_publickey="J5hkNQTVi18NCEMSGBsMY9mdtHfb5JFpUc4bHE7D89ft",
        slippage_bps=100,
        jito_tip_lamports=1000000,
    )
    assert "swapTransaction" in swap_tx_resp


@pytest.mark.asyncio
async def test_get_swap_instructions():
    jupiter_api = JupiterAPI()
    swap_instructions = await jupiter_api.get_swap_instructions(
        input_mint="So11111111111111111111111111111111111111112",
        output_mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
        amount=100,
        slippage_bps=100,
        user_publickey="J5hkNQTVi18NCEMSGBsMY9mdtHfb5JFpUc4bHE7D89ft",
    )
    assert "computeBudgetInstructions" in swap_instructions
