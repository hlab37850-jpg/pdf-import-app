[app]
title = PDF Import App
package.name = pdfimportapp
package.domain = org.pdfimport
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0.0
requirements = python3,kivy==2.2.1,pdfminer.six==20221105,arabic-reshaper==3.0.0,python-bidi==0.4.2,langdetect==1.0.9
orientation = portrait
fullscreen = 0
android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE
android.api = 33
android.minapi = 24
android.ndk = 25b
android.arch = arm64-v8a
android.private_storage = True
android.presplash_color = #6200EE
android.accept_sdk_license = True
android.allow_backup = True
android.skip_update = False

[buildozer]
log_level = 2
warn_on_root = 1
