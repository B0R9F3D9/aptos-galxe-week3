from aptos_sdk.transactions import TransactionArgument, Serializer, EntryFunction
from aptos_sdk.account import AccountAddress

from loguru import logger
from random import choice, randint

from .aptos import Aptos
from utils.decorators import retry
from config import BID_NFTS, MERCATO_BID_CONTRACT_V1, MERCATO_BID_CONTRACT_V2


class Mercato:
    def __init__(self, acc: Aptos) -> None:
        self.acc: Aptos = acc

    @retry
    async def bid(self) -> None:
        nft_name = choice(list(BID_NFTS.keys()))
        nft_address = BID_NFTS[nft_name]
        nft_address = AccountAddress.from_str(nft_address)
        bid_amount = randint(1, 333)
        bid_quantity = 1

        logger.info(f'{self.acc.info} | Делаю бид на Mercato на "{nft_name}" нфт')

        ty_args = []

        args = [
            TransactionArgument(nft_address, Serializer.struct),
            TransactionArgument(bid_amount, Serializer.u64),
            TransactionArgument(bid_quantity, Serializer.u64),
        ]

        if 'V2' in nft_name:
            contract = MERCATO_BID_CONTRACT_V2
            func = 'collection_bids'
        else:
            args.insert(1, TransactionArgument(nft_name, Serializer.str))
            contract = MERCATO_BID_CONTRACT_V1
            func = 'collection_bid'

        payload = EntryFunction.natural(
            module=contract,
            function=func,
            ty_args=ty_args,
            args=args
        )

        raw_txn = await self.acc.get_raw_txn(payload)
        await self.acc.send_txn(raw_txn)
        