# Keep Chaquopy classes
-keep class com.chaquo.python.** { *; }
-keep class com.pdfimport.app.** { *; }

# Keep Python classes
-keep class org.python.** { *; }

# Optimizations
-optimizations !code/simplification/arithmetic,!field/*,!class/merging/*
-allowaccessmodification
