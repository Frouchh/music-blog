@echo off
rem Ежедневное резервное копирование интернет-магазина.
rem Запускается Планировщиком заданий Windows ежедневно в 03:00 из корня проекта.
rem Хранятся копии за последние 14 дней на отдельном диске.

set BACKUP_DIR=D:\backup\audio_shop
set STAMP=%date:~6,4%-%date:~3,2%-%date:~0,2%
mkdir "%BACKUP_DIR%\%STAMP%" 2>nul

rem 1. Дамп базы данных (без блокировки таблиц InnoDB)
mysqldump -u shop_user -p%DB_PASSWORD% --single-transaction --routines audio_shop > "%BACKUP_DIR%\%STAMP%\audio_shop.sql"

rem 2. Архив файлов: демофрагменты, обложки и полные аудиофайлы
tar -a -cf "%BACKUP_DIR%\%STAMP%\files.zip" media protected_media

rem 3. Удаление копий старше 14 дней
forfiles /p "%BACKUP_DIR%" /d -14 /c "cmd /c if @isdir==TRUE rmdir /s /q @path" 2>nul
