@echo off
echo Экспорт базы данных...
mysqldump -u root music_blog > music_blog_dump.sql
echo Готово! Файл: music_blog_dump.sql
pause