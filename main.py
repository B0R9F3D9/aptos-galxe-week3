from settings import *
from modules_settings import *
from utils.sleep import sleep
from utils.pk_from_mnemonic import mnemonic_to_private_key

import asyncio, sys
from loguru import logger
from datetime import datetime
from string import ascii_letters, digits
from random import choices, shuffle
from questionary import Choice, select
from concurrent.futures import ThreadPoolExecutor
from better_automation.twitter import TwitterAccount

date_now = datetime.now().strftime("%d-%m-%Y")
format = '<white>{time:HH:mm:ss}</white> | <bold><level>{level: <7}</level></bold> | <level>{message}</level>'
logger.remove()
logger.add(sys.stderr, format=format)
logger.add(f'logs/{date_now}.log', format=format, level='INFO')


def get_accs(accs: list[Aptos]) -> list[Aptos]:
    if len(accs) == 1:
        return [accs[0]]
    print(
        'Выберите аккаунты для работы. Пример: \n'
        '1 — для выбора только первого аккаунта\n'
        '1,2,3 — для выбора первого, второго и третьего аккаунта\n'
        '1-3 — для выбора аккаунтов от первого до третьего включительно\n'
        'all — для выбора всех аккаунтов')
    result = input('Введите ваш выбор: ')
    try:
        if result == 'all':
            return accs 
        elif ',' in result:
            return [accs[int(i) - 1] for i in result.split(',')]
        elif '-' in result:
            return accs[int(result.split('-')[0]) - 1:int(result.split('-')[1])]
        elif '-' not in result and ',' not in result:
            return [accs[int(result) - 1]]
    except Exception:
        logger.critical('Произошла ошибка при выборе аккаунтов!')
        exit()

async def get_module() -> callable or str:
    result = await select(
        message="Выберите модуль для работы: ",
        instruction='(используйте стрелочки для навигации)',
        choices=[
            Choice("1) Минт нфт на Wapal", mint_wapal),
            Choice("2) Бид нфт на Mercato", bid_mercato),
            Choice("3) Бид нфт на Topaz", bid_topaz),
            Choice("4) Авто минт/бид", complete_bid_mint),
            Choice("4) Чекер кошельков", checker_module),
            Choice("5) Подписаться на каналы Twitter", twitter_module),
            Choice("6) Заполнить гугл форму", google_form_module),
            Choice("🔙 Вернуться к выбору аккаунтов", 'back'),
            Choice("❌ Выход", "exit"),
        ],
        qmark="\n❓ ",
        pointer="👉 "
    ).ask_async()
    return result

async def main(accs: list[Aptos]) -> None:
    module = await get_module()
    if module == checker_module:
        await checker_module(accs)
        return
    elif module == twitter_module:
        await twitter_module(TWITTERS)
        return
    elif module == google_form_module:
        await google_form_module(accs, EMAILS)
        return
    elif module == 'back':
        return True
    elif module == 'exit':
        print('\n👋👋👋')
        exit()

    module_settings = await get_module_settings(module)
    for acc in accs:
        await module(acc, module_settings)
        if acc != accs[-1]:
            await sleep(*SLEEP_AFTER_ACC)

def create_aptos(id_wallet_tuple):
    _id, wallet = id_wallet_tuple
    if not wallet.startswith('0x'):
        wallet = '0x' + mnemonic_to_private_key(wallet).hex()
    return Aptos(_id, wallet)


if __name__ == "__main__":
    if sys.version_info >= (3, 8) and sys.platform.lower().startswith("win"):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    with open('data/wallets.txt', 'r') as file:
        WALLETS = [x.strip() for x in file.readlines()]
    with ThreadPoolExecutor(max_workers=7) as executor: 
        futures = [executor.submit(create_aptos, (_id, wallet)) for _id, wallet in enumerate(WALLETS, 1)]
        WALLETS = [future.result() for future in futures]

    with open('data/twitters.txt', 'r') as file:
        TWITTERS = [x.strip() for x in file.readlines()]
    for twitter in TWITTERS:
        if ':' in twitter: cookie = twitter.split(':')[4]
        else: cookie = twitter
        TWITTERS[TWITTERS.index(twitter)] = TwitterAccount.from_cookies(cookie, base64=True)

    with open('data/emails.txt', 'r') as file:
        EMAILS = [x.strip() for x in file.readlines()]

    logger.info(f'Найдено: {len(WALLETS)} кошельков, {len(TWITTERS)} твиттеров, {len(EMAILS)} почт')
    if SHUFFLE_WALLETS: 
        shuffle(WALLETS)
        logger.warning('Список кошельков перемешан')
    if USE_PRESETS:
        logger.warning('Используются пресеты!')
    if USE_GENERATED_EMAILS:
        EMAILS = [None] * len(WALLETS)
        for i in range(len(WALLETS)):
            EMAILS[i] = f"{''.join(choices(ascii_letters + digits, k=randint(5, 15)))}@gmail.com"
        logger.warning('Используются сгенерированные почты!')

    try:
        loop = asyncio.get_event_loop() 
        loop.run_until_complete(checker_module(WALLETS)) 
        selected_accs = get_accs(WALLETS)
        while True:
            result = loop.run_until_complete(main(selected_accs)) 
            if result:
                loop.run_until_complete(checker_module(WALLETS)) 
                selected_accs = get_accs(WALLETS)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logger.critical(e)
    finally:
        loop.close()

    print('\n👋👋👋')
