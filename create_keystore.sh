#!/bin/bash
keytool -genkeypair -v \
  -keystore keystore/release.keystore \
  -alias pdfimport \
  -keyalg RSA \
  -keysize 2048 \
  -validity 10000 \
  -storepass pdfimport2024 \
  -keypass pdfimport2024 \
  -dname "CN=PDF Import, OU=App, O=PDFImport, L=City, S=State, C=US"
