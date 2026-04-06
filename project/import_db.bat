@echo off
echo Импорт базы данных...
mysql -u root -e "DROP DATABASE IF EXISTS music_blog"
mysql -u root -e "CREATE DATABASE music_blog CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
mysql -u root music_blog < music_blog_dump.sql
echo Готово!
pause