from aptos_sdk.transactions import TransactionArgument, Serializer, EntryFunction
from aptos_sdk.account import AccountAddress

from loguru import logger
from random import choice

from .aptos import Aptos
from utils.decorators import retry
from config import WAPAL_MINT_CONTRACT, WAPAL_MINT_NFTS


class Wapal:
    def __init__(self, acc: Aptos) -> None:
        self.acc: Aptos = acc

    @retry
    async def mint(self) -> None:
        nft_address = choice(WAPAL_MINT_NFTS)

        logger.info(f'{self.acc.info} | Минчу нфт на Wapal')

        ty_args = []

        args = [
            TransactionArgument(AccountAddress.from_str(nft_address), Serializer.struct),
        ]

        payload = EntryFunction.natural(
            module=WAPAL_MINT_CONTRACT,
            function='mint_script',
            ty_args=ty_args,
            args=args
        )

        raw_txn = await self.acc.get_raw_txn(payload)
        await self.acc.send_txn(raw_txn)
        