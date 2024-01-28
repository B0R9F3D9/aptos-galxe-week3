# Aptos 3 неделя Galxe
![image](https://i.postimg.cc/yY5Rg75V/photo-2024-01-28-14-41-33.jpg)

## Настройка
* В файл `data/twitters.txt` вписываем base64 куки от твиттера с новой строки или твиттеры в формате `логин:пароль:почта:пароль:кукиbase64`
* В файл `data/wallets.txt` вписываем приватные фразы или ключи каждый с новой строки
* В файл `data/emails.txt` вписываем почты для заполнения гугл формы
* В файле `settings.py` выставляем настройки, там каждый пункт подписан

# Установка:
#### *Чтобы были эмодзи и всё отображалось корректно лучше использовать VS Code или Windows Terminal*
Открываем cmd в папке скрипта и прописываем:
1. `cd путь/к/проекту`
2. `python3 -m venv venv`
3. MacOS/Linux `source venv/bin/activate` | Windows `.\venv\Scripts\activate`
4. `pip install -r requirements.txt`

# Запуск:
```
    python main.py
```
