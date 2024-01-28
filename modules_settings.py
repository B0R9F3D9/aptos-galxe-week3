import aiohttp
import time
from loguru import logger
from random import randint
from fake_useragent import UserAgent
from better_automation.twitter import TwitterClient, TwitterAccount

from modules import *
from settings import *
from utils.sleep import sleep
from config import TWITTER_FOLLOW_IDS, GOOGLE_FORM_URL


async def get_module_settings(module: callable) -> list:
    if USE_PRESETS:
        return [MIN_TX_COUNT, MAX_TX_COUNT]
    else:
        min_tx_count = int(input('Введите минимальное количество транзакций: '))
        max_tx_count = int(input('Введите максимальное количество транзакций: ')) 
        return [min_tx_count, max_tx_count]


async def mint_wapal(acc: Aptos, module_settings: list) -> None:
    tx_count = randint(module_settings[0], module_settings[1])
    wapal = Wapal(acc)
    for i in range(tx_count):
        await wapal.mint()
        if i < tx_count - 1:
            await sleep(*SLEEP_BETWEEN_TXS)


async def bid_mercato(acc: Aptos, module_settings: list) -> None:
    tx_count = randint(module_settings[0], module_settings[1])
    mercato = Mercato(acc)
    for i in range(tx_count):
        await mercato.bid()
        if i < tx_count - 1:
            await sleep(*SLEEP_BETWEEN_TXS)


async def bid_topaz(acc: Aptos, module_settings: list) -> None:
    tx_count = randint(module_settings[0], module_settings[1])
    topaz = Topaz(acc)
    for i in range(tx_count):
        await topaz.bid()
        if i < tx_count - 1:
            await sleep(*SLEEP_BETWEEN_TXS)


async def checker_module(accs: list[Aptos]) -> None:
    checker = Checker(accs)
    await checker.check()


async def twitter_module(twitters: list[TwitterAccount]) -> None:
    for twitter in twitters:
        client = TwitterClient(twitter)
        me = await client.request_user_data()
        for channel in TWITTER_FOLLOW_IDS:
            await client.follow(channel)
        logger.success(f'@{me.username} Успешно подписался на все твиттеры!')
        client.close()


async def google_form_module(accs: list[Aptos], emails: list[str]) -> None:
    url = GOOGLE_FORM_URL + '/formResponse?pli=1'
    ua = UserAgent()
    for acc, email in zip(accs, emails):
        address = acc.address
        data = {
            "emailAddress": email,
            "entry.908064693": address,
            "dlut": int(time.time() * 1000)
        }
        headers = {'User-Agent': ua.random}
        async with aiohttp.ClientSession() as session:
            async with session.post(url=url, data=data, headers=headers) as resp:
                if resp.status == 200:
                    logger.success(f'{acc.info} | Успешно заполнил форму на {email}!')
                else:
                    logger.error(f'{acc.info} | Не удалось заполнить форму | Ошибка {resp.status}!')
