package com.pdfimport.app

import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.provider.OpenableColumns
import android.widget.Button
import android.widget.ProgressBar
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.chaquo.python.Python
import com.chaquo.python.android.AndroidPlatform
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.io.File
import java.io.FileOutputStream

class MainActivity : AppCompatActivity() {
    
    private lateinit var progressBar: ProgressBar
    private lateinit var statusText: TextView
    private lateinit var selectButton: Button
    private lateinit var processButton: Button
    
    private var selectedPdfUri: Uri? = null
    private var selectedPdfPath: String? = null
    private var selectedFileName: String = "document.pdf"
    
    private val PICK_PDF_REQUEST = 1
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        
        initializeViews()
        initializePython()
        setupListeners()
    }
    
    private fun initializeViews() {
        progressBar = findViewById(R.id.progressBar)
        statusText = findViewById(R.id.statusText)
        selectButton = findViewById(R.id.selectButton)
        processButton = findViewById(R.id.processButton)
        
        progressBar.visibility = ProgressBar.INVISIBLE
        processButton.isEnabled = false
    }
    
    private fun initializePython() {
        if (!Python.isStarted()) {
            Python.start(AndroidPlatform(this))
        }
    }
    
    private fun setupListeners() {
        selectButton.setOnClickListener {
            openFilePicker()
        }
        
        processButton.setOnClickListener {
            selectedPdfPath?.let { path ->
                processPDF(path)
            }
        }
    }
    
    private fun openFilePicker() {
        val intent = Intent(Intent.ACTION_OPEN_DOCUMENT).apply {
            addCategory(Intent.CATEGORY_OPENABLE)
            type = "application/pdf"
        }
        startActivityForResult(intent, PICK_PDF_REQUEST)
    }
    
    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        
        if (requestCode == PICK_PDF_REQUEST && resultCode == RESULT_OK) {
            data?.data?.let { uri ->
                selectedPdfUri = uri
                selectedFileName = getFileName(uri)
                copyPdfToInternalStorage(uri) { path ->
                    selectedPdfPath = path
                    runOnUiThread {
                        processButton.isEnabled = true
                        statusText.text = "PDF selected: $selectedFileName"
                        statusText.setTextColor(getColor(android.R.color.holo_green_dark))
                    }
                }
            }
        }
    }
    
    private fun copyPdfToInternalStorage(uri: Uri, callback: (String) -> Unit) {
        lifecycleScope.launch(Dispatchers.IO) {
            try {
                val inputStream = contentResolver.openInputStream(uri)
                val outputFile = File(cacheDir, selectedFileName)
                
                inputStream?.use { input ->
                    FileOutputStream(outputFile).use { output ->
                        input.copyTo(output)
                    }
                }
                
                withContext(Dispatchers.Main) {
                    callback(outputFile.absolutePath)
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    Toast.makeText(this@MainActivity, "Error copying file: ${e.message}", Toast.LENGTH_LONG).show()
                    statusText.text = "Error: ${e.message}"
                    statusText.setTextColor(getColor(android.R.color.holo_red_dark))
                }
            }
        }
    }
    
    private fun getFileName(uri: Uri): String {
        var fileName = "document.pdf"
        contentResolver.query(uri, null, null, null, null)?.use { cursor ->
            if (cursor.moveToFirst()) {
                val nameIndex = cursor.getColumnIndex(OpenableColumns.DISPLAY_NAME)
                if (nameIndex >= 0) {
                    fileName = cursor.getString(nameIndex)
                }
            }
        }
        return fileName
    }
    
    private fun processPDF(pdfPath: String) {
        lifecycleScope.launch {
            try {
                progressBar.visibility = ProgressBar.VISIBLE
                progressBar.isIndeterminate = true
                statusText.text = "Processing PDF..."
                statusText.setTextColor(getColor(android.R.color.holo_blue_dark))
                processButton.isEnabled = false
                selectButton.isEnabled = false
                
                val result = withContext(Dispatchers.IO) {
                    PythonPDFProcessor.processPDF(pdfPath)
                }
                
                progressBar.visibility = ProgressBar.INVISIBLE
                statusText.text = "Processing complete!"
                statusText.setTextColor(getColor(android.R.color.holo_green_dark))
                processButton.isEnabled = true
                selectButton.isEnabled = true
                
                showResults(result)
            } catch (e: Exception) {
                progressBar.visibility = ProgressBar.INVISIBLE
                statusText.text = "Error: ${e.message}"
                statusText.setTextColor(getColor(android.R.color.holo_red_dark))
                processButton.isEnabled = true
                selectButton.isEnabled = true
                Toast.makeText(this@MainActivity, "Processing error: ${e.message}", Toast.LENGTH_LONG).show()
            }
        }
    }
    
    private fun showResults(result: PDFProcessingResult) {
        val intent = Intent(this, ResultsActivity::class.java)
        intent.putExtra("result_json", result.toJson())
        startActivity(intent)
    }
}
