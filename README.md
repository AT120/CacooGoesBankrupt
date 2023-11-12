# Конфигурация  
Для конфигурации бота нужно в той же папке, где находится файл app.py,  создать файл с именем config.json. (В качестве примера прикреплен config.example.json, можно просто преименовать его)  

Используемые опции:  
- "cacoo-api-key" - ключ api от аккаунта, на котором будут создаваться диаграммы
- "discord-token" - токен бота дискорда, можно оставить токен из примера или изменить если необходим полный контроль на ботом
- "database-file" - изменить путь до файла с базой данных. Можно не трогать
- "cacoo-folder-name" - имя папки на аккаунте cacoo, в которой будут храниться диаграммы. Папка должна создана заранее
- "log-level" - уровень логирования. Может быть:
    - DEBUG
    - INFO
    - WARNING
    - ERROR
    - CRITICAL
- "admin-discord-id" - идентификатор пользователя дискорда, который будет иметь доступ к текстовым коммандам администратора (см. пункт комманды)
- "whitelist-server-id" - идентификатор сервера, пользователи которого смогут создавать диаграммы, используя бота.
> для получения admin-discord-id и whitelist-server-id удобно будет включить режим разработчика в клиенте discord

# Где взять API ключ Cacoo

1. Перейти на <https://cacoo.com>
> Далее можно заменить в адресной строке "recent" на "settings/integrations/developer-tools" и перейти к шагу 6
2. Нажать по своему профилю справа сверху
3. Нажать "Cacoo settings"
4. Слева выбрать раздел "Integrations"
5. Справа сверху небольшая ссылочка "Developer Tools"
6. Generate API Key - если ключ не создавался до этого
7. Скопировать ключик
8. Вставить его в config.json

# Запуск бота
- Создать и заполнить файл config.json
- Установить зависимости из файла requirements.txt:  
```pip install -r requirements.txt```
- Запустить приложение:  
```python app.py```

# Комманды
## Текстовые команды администратора
Для их использования нужно тегнуть бота и написать название команды
- reload_whitelist - перезагрузить пользователей с whitelist-сервера 
- sync_commands - синхронизировать слэш-комманды с серверами discord
- reset_cacoo_cache - перезагрузить id организации и id папки с серверов cacoo
- get_guilds - посмотреть, на какие сервера бот добавлен и их идентификаторы

## Слэш-команды администратора
Использование этих комманд разрешено только в каналах whitelist-сервера. Ограничение доступа к этим командам среди пользователей whitelist-сервера реализованно через встроенный функционал ролей дискорда. Это значит, что администратор whitelist-сервера должен сам ограничить доступ к определенным командам у некоторых ролей или пользователей. 
- userstats - статистика использования бота, сгруппированная по пользователям
-  unusedstats - давно неиспользовавшиеся диаграммы
> не стоит использовать эту комманду слишком часто, т.к. она требует объемного запроса к Cacoo по каждой диаграмме в системе
- admindel - удалить чужую диаграмму
- admindia - посмотреть диаграммы другого пользователя


## Слэш-команды пользователя
Эти команды могут быть использованны в личной переписке с ботом.
- new - создать новую диаграмму
- del - удалить диаграмму
- dia - просмотр своих диаграмм

