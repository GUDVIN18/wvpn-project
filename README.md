
По всем вопроам можете обращаться в тг: @Dmitriy_prog
# wvpn-project

проект w vpn написанный на Python + fastapi (логика с create/update ключей) + django (админка / БД) + мой конструктор по ботам bot_builder

# Сделать dump
pg_dump \
  -h localhost \
  -U admin \
  -d bot_db_out \
  -F c \
  -b \
  -v \
  -f bot_db_out_full.dump

# Восстановление дампа
pg_restore \
  -h localhost \
  -U admin \
  -d bot_db_out \
  -v \
  bot_db_out_full.dump

