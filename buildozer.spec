[app]
title = Fitness Tracker
package.name = fitnesstracker
package.domain = org.example
source.dir = .
source.include_exts = py,json,png,jpg,kv  # добавил .kv на случай использования
version = 1.0
requirements = python3,kivy  # убрал datetime, версия Kivy не указана (или используйте kivy==2.3.0)
orientation = portrait
android.api = 33
android.minapi = 21
android.ndk = 23b  # более стабильная версия NDK
android.permissions = INTERNET
