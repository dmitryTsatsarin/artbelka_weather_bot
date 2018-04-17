
	
**Регламент первой установки**
-пробросить симлинк nginx конфигурации в sites-enabled




1) обновить исходники
2) установить пакеты через pip
3) выполнить миграции
4) собрать статику
5) создать таблицу кэша (python manage.py createcachetable)
6) перечитать конфиги supervisor
7) стартануть web-сервер через supervisor
8) посавить руками wkhtmltoimage (не меньше 0.12.4)
9) проверить работоспособность скриншотов погоды 



**Регламент обновления (ручное)**
1) обновить исходники
2) установить пакеты через pip   # pip install -r ./requirements.txt
3) сделать бекап БД              # pg_dump -h localhost -O shop_bot_prod -f /home/webrunner/backups/$(date +"%Y-%m-%d_%H-%M")
4) выполнить миграции            # python manage.py migrate
5) обновить конфиг supervisor                          # sudo supervisorctl reread && sudo supervisorctl update
6) перезагрузить web-сервер через supervisor           # sudo supervisorctl restart shop_bot:


**ключевые части кода для работы**

more_command = create_uri(TextCommandEnum.GET_CATALOG, catalog_id=catalog_id, offset=new_offset)

query_dict = get_query_dict(call_data)
catalog_id_str = query_dict.get('catalog_id')



