# Перемешать кошельки
SHUFFLE_WALLETS: bool = False

# Задержка между аккаунтами
SLEEP_AFTER_ACC: tuple[int, int] = (5, 15)

# Задержка между транзакциями
SLEEP_BETWEEN_TXS: tuple[int, int] = (3, 5)

# Количество попыток для совершения транзакции
RETRY_COUNT: int = 1

# Выводить ссылки на транзакции
PRINT_LINK_TO_TXS: bool = True

# Использовать сгенерированные почты
USE_GENERATED_EMAILS: bool = True

#-------------Преднастройки для модулей-------------
USE_PRESETS: bool = True # Использовать преднастройки
MIN_TX_COUNT: int = 1 # Минимальное количество транзакций
MAX_TX_COUNT: int = 1 # Максимальное количество транзакций
#---------------------------------------------------

# Прочее
RPC: str = 'https://aptos-mainnet.pontem.network/v1'
EXPLORER: str = 'https://explorer.aptoslabs.com/txn/'
