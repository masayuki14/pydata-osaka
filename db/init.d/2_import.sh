cd /docker-entrypoint-initdb.d/

mysql -u root -p$MYSQL_ROOT_PASSWORD pydata < pydata.dump
