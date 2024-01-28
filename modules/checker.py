import aiohttp
import asyncio
from tabulate import tabulate

from .aptos import Aptos
from config import *
from settings import RPC

contracts = [
    WAPAL_MINT_CONTRACT,
    MERCATO_BID_CONTRACT_V1,
    MERCATO_BID_CONTRACT_V2,
    TOPAZ_BID_CONTRACT_V1,
    TOPAZ_BID_CONTRACT_V2
]


class Checker:
    def __init__(self, accs: list[Aptos]) -> None:
        self.accs: list[Aptos] = accs
        self.session: aiohttp.ClientSession = None
        self.apt_price: float = None

    async def get_acc_info(self, acc: Aptos) -> dict:
        mint = False
        bid = False

        tx_count = await acc.client.account_sequence_number(acc.account_address)
        balance = (await acc.client.account_balance(acc.account_address)) / 10**8
        balance_usd = balance * self.apt_price

        async with self.session.get(f'{RPC}/accounts/{acc.address}/transactions') as resp:
            data = await resp.json()
        for tx in data:
            tx_func = tx['payload']['function']
            if tx_func in contracts:
                if tx_func == WAPAL_MINT_CONTRACT:
                    mint = True
                else:
                    bid = True

        return {
            '№': acc.id,
            'Адрес': f"{acc.address[:5]}...{acc.address[-5:]}",
            'Txs': tx_count,
            'APT': f'{balance:.4f}',
            'APT $': f'{balance_usd:.3f}',
            'Минт': '✅' if mint else '❌',
            'Бид': '✅' if bid else '❌',
        }

    async def check(self) -> None:
        async with aiohttp.ClientSession() as self.session:
            self.apt_price = await self.accs[0].get_apt_price()
            tasks = [self.get_acc_info(acc) for acc in self.accs]
            result = await asyncio.gather(*tasks)

        print(tabulate(result, headers='keys', tablefmt='rounded_grid'))