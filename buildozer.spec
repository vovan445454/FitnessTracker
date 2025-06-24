[app]
title = Fitness Tracker
package.name = fitnesstracker
package.domain = org.example
source.dir = .
source.include_exts = py,json,png,jpg  # добавить изображения
version = 1.0
requirements = python3,kivy,datetime  # исправьте зависимости
orientation = portrait
osx.python_version = 3
osx.kivy_version = 2.3.0  # обновите версию
android.api = 33
android.minapi = 21
android.ndk = 25b  # новая версия NDK
p4a.branch = 2023.06.11  # стабильная ветка
android.permissions = INTERNET
log_level = 2
requirements = python3==3.10.13, kivy==2.3.0, datetime
p4a.branch = master
android.ndk = 25b
