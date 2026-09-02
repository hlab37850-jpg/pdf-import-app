package com.pdfimport.webview;

import android.app.Activity;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.webkit.JavascriptInterface;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.annotation.SuppressLint;
import android.util.Base64;
import android.util.Log;
import android.widget.Toast;

import java.io.ByteArrayOutputStream;
import java.io.InputStream;

public class MainActivity extends Activity {
    private WebView webView;
    private static final int PICK_PDF_REQUEST = 1;
    private static final String TAG = "PDFImport";
    private String pendingFileData = null;
    
    @SuppressLint({"SetJavaScriptEnabled", "JavascriptInterface"})
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        
        webView = new WebView(this);
        webView.setWebViewClient(new WebViewClient());
        
        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setAllowFileAccess(true);
        settings.setAllowContentAccess(true);
        settings.setDomStorageEnabled(true);
        
        // إضافة JavaScript Interface للتواصل مع HTML
        webView.addJavascriptInterface(new JavaScriptInterface(), "AndroidBridge");
        
        webView.loadUrl("file:///android_asset/www/index.html");
        
        setContentView(webView);
    }
    
    // JavaScript Interface للتواصل مع HTML
    private class JavaScriptInterface {
        @JavascriptInterface
        public void openFilePicker() {
            runOnUiThread(new Runnable() {
                @Override
                public void run() {
                    Intent intent = new Intent(Intent.ACTION_GET_CONTENT);
                    intent.addCategory(Intent.CATEGORY_OPENABLE);
                    intent.setType("application/pdf");
                    startActivityForResult(Intent.createChooser(intent, "Select PDF"), PICK_PDF_REQUEST);
                }
            });
        }
        
        @JavascriptInterface
        public String getSelectedFile() {
            return pendingFileData;
        }
        
        @JavascriptInterface
        public void clearSelectedFile() {
            pendingFileData = null;
        }
    }
    
    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        
        if (requestCode == PICK_PDF_REQUEST && resultCode == Activity.RESULT_OK) {
            if (data != null && data.getData() != null) {
                try {
                    Uri uri = data.getData();
                    byte[] fileBytes = readBytes(uri);
                    String base64 = Base64.encodeToString(fileBytes, Base64.NO_WRAP);
                    pendingFileData = base64;
                    
                    // إرسال الملف إلى JavaScript
                    String js = "javascript:receiveFile('" + base64 + "')";
                    webView.post(new Runnable() {
                        @Override
                        public void run() {
                            webView.evaluateJavascript(js, null);
                        }
                    });
                    
                } catch (Exception e) {
                    Log.e(TAG, "Error reading file", e);
                    Toast.makeText(this, "Error: " + e.getMessage(), Toast.LENGTH_LONG).show();
                }
            }
        }
    }
    
    private byte[] readBytes(Uri uri) throws Exception {
        InputStream inputStream = getContentResolver().openInputStream(uri);
        ByteArrayOutputStream byteBuffer = new ByteArrayOutputStream();
        
        byte[] buffer = new byte[1024 * 1024]; // 1MB buffer
        int len;
        while ((len = inputStream.read(buffer)) != -1) {
            byteBuffer.write(buffer, 0, len);
        }
        
        return byteBuffer.toByteArray();
    }
    
    @Override
    public void onBackPressed() {
        if (webView.canGoBack()) {
            webView.goBack();
        } else {
            super.onBackPressed();
        }
    }
}
