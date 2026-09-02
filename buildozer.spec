[app]
title = PDF Import App
package.name = pdfimportapp
package.domain = org.pdfimport
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version = 1.0.0
requirements = python3,kivy,PyMuPDF==1.22.5,pdfminer.six==20221105,Pillow==9.5.0,numpy==1.24.3,opencv-python-headless==4.8.0.74,arabic-reshaper==3.0.0,python-bidi==0.4.2,langdetect==1.0.9,pandas==2.0.3,loguru==0.7.2
orientation = portrait
fullscreen = 0
android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE
android.api = 33
android.minapi = 24
android.ndk = 25b
android.arch = arm64-v8a
android.entrypoint = org.kivy.android.PythonActivity
android.private_storage = True
android.presplash_color = #6200EE
android.icon = icon.png
android.presplash = presplash.png

[buildozer]
log_level = 2
warn_on_root = 1
