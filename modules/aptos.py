from aptos_sdk.account import Account
from aptos_sdk.async_client import RestClient
from aptos_sdk.authenticator import Authenticator, Ed25519Authenticator
from aptos_sdk.transactions import RawTransaction, SignedTransaction, TransactionPayload

from loguru import logger
import aiohttp
import time

from settings import RPC, EXPLORER, PRINT_LINK_TO_TXS


class Aptos(Account):
    def __init__(self, _id: int, private_key: str) -> None:
        try:
            self.account: Account = Account.load_key(private_key)
        except:
            logger.error(f'[№{_id}] не валидный приватный ключ')
            return
        self.client = RestClient(RPC)
        self.address: str = str(self.account.address())
        self.id: int = _id
        self.info: str = f'[№{_id} - {self.address[:5]}...{self.address[-5:]}]'
        self.explorer: str = EXPLORER
        super().__init__(self.account.account_address, self.account.private_key)

    async def get_apt_price(self) -> float:
        async with aiohttp.ClientSession() as session:
            async with session.get('https://www.binance.com/api/v3/ticker/price?symbol=APTUSDT') as resp:
                return float((await resp.json())['price'])
            
    async def get_raw_txn(self, payload: dict) -> RawTransaction | None:
        raw_txn =  RawTransaction(
            self.account.account_address,
            await self.client.account_sequence_number(self.account.account_address),
            TransactionPayload(payload),
            1000, # max_gas_amount
            100, # gas_unit_price
            int(time.time()) + 60,
            chain_id=1,
        )
        simulated_txn = (await self.client.simulate_transaction(raw_txn, self.account, True))[0]
        if simulated_txn["vm_status"] != 'Executed successfully':
            logger.error(f'Не удалось создать транзакцию: {simulated_txn["vm_status"]}')
            return
        raw_txn.max_gas_amount = int(simulated_txn["max_gas_amount"])
        raw_txn.gas_unit_price = int(simulated_txn["gas_unit_price"])
        return raw_txn

    async def send_txn(self, raw_txn: RawTransaction) -> None:
        if not raw_txn:
            return
        signature = self.account.sign(raw_txn.keyed())
        auth = Authenticator(Ed25519Authenticator(self.account.public_key(), signature))
        tx_hash = await self.client.submit_bcs_transaction(SignedTransaction(raw_txn, auth))
        tx_result = await self.client.wait_for_transaction(tx_hash)
        if tx_result is None:
            logger.success(f'{self.info} | Транзакция успешна! {self.explorer+tx_hash if PRINT_LINK_TO_TXS else ""}')
