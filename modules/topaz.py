from aptos_sdk.transactions import TransactionArgument, Serializer, EntryFunction, \
    TypeTag, StructTag
from aptos_sdk.account import AccountAddress

from loguru import logger
from random import choice, randint
from time import time

from .aptos import Aptos
from utils.decorators import retry
from config import TOPAZ_BID_CONTRACT_V1, TOPAZ_BID_CONTRACT_V2, TOPAZ_FEE_SCHEDULE, BID_NFTS


class Topaz:
    def __init__(self, acc: Aptos) -> None:
        self.acc: Aptos = acc

    @retry
    async def bid(self) -> None:
        nft_name = choice(list(BID_NFTS.keys()))
        nft_address = BID_NFTS[nft_name]
        nft_address = AccountAddress.from_str(nft_address)
        fee_schedule = AccountAddress.from_str(TOPAZ_FEE_SCHEDULE)
        bid_amount = randint(88, 345)
        bid_quantity = 1
        bid_hours = randint(1, 24)
        time_expiration = (int(time()) + (bid_hours * 3600)) * 1000 * 1000
        logger.info(f'{self.acc.info} | Делаю бид на Topaz на "{nft_name}" нфт')

        ty_args = [
            TypeTag(StructTag.from_str('0x1::aptos_coin::AptosCoin'))
        ]

        if 'V2' in nft_name:
            contract = TOPAZ_BID_CONTRACT_V2
            func = 'init_for_tokenv2_entry'
            args = [
                TransactionArgument(nft_address, Serializer.struct),
                TransactionArgument(fee_schedule, Serializer.struct),
                TransactionArgument(bid_amount, Serializer.u64),
                TransactionArgument(bid_quantity, Serializer.u64),
                TransactionArgument(time_expiration, Serializer.u64),
            ]

        else:
            contract = TOPAZ_BID_CONTRACT_V1
            func = 'bid'
            args = [
                TransactionArgument(bid_amount, Serializer.u64),
                TransactionArgument(bid_quantity, Serializer.u64),
                TransactionArgument(time_expiration, Serializer.u64),
                TransactionArgument(nft_address, Serializer.struct),
                TransactionArgument(nft_name, Serializer.str),
            ]

        payload = EntryFunction.natural(
            module=contract,
            function=func,
            ty_args=ty_args,
            args=args
        )

        raw_txn = await self.acc.get_raw_txn(payload)
        await self.acc.send_txn(raw_txn)
        
