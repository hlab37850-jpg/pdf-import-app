package com.pdfimport.app

import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.content.Intent
import android.os.Bundle
import android.os.Environment
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import org.json.JSONObject
import java.io.File
import java.io.FileOutputStream
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

class ResultsActivity : AppCompatActivity() {
    
    private lateinit var confidenceValue: TextView
    private lateinit var pagesValue: TextView
    private lateinit var tablesValue: TextView
    private lateinit var imagesValue: TextView
    private lateinit var methodValue: TextView
    private lateinit var timeValue: TextView
    private lateinit var textContent: EditText
    private lateinit var copyButton: Button
    private lateinit var saveButton: Button
    
    private lateinit var processingResult: PDFProcessingResult
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_results)
        
        initializeViews()
        setupToolbar()
        loadResult()
        setupListeners()
    }
    
    private fun initializeViews() {
        confidenceValue = findViewById(R.id.confidenceValue)
        pagesValue = findViewById(R.id.pagesValue)
        tablesValue = findViewById(R.id.tablesValue)
        imagesValue = findViewById(R.id.imagesValue)
        methodValue = findViewById(R.id.methodValue)
        timeValue = findViewById(R.id.timeValue)
        textContent = findViewById(R.id.textContent)
        copyButton = findViewById(R.id.copyButton)
        saveButton = findViewById(R.id.saveButton)
    }
    
    private fun setupToolbar() {
        val toolbar = findViewById<androidx.appcompat.widget.Toolbar>(R.id.toolbar)
        toolbar.setNavigationOnClickListener {
            finish()
        }
    }
    
    private fun loadResult() {
        val resultJson = intent.getStringExtra("result_json")
        
        if (resultJson != null) {
            val jsonObject = JSONObject(resultJson)
            
            processingResult = PDFProcessingResult(
                text = jsonObject.optString("text", ""),
                confidence = jsonObject.optDouble("confidence", 0.0),
                pagesProcessed = jsonObject.optInt("pages_processed", 0),
                tablesExtracted = jsonObject.optInt("tables_extracted", 0),
                imagesExtracted = jsonObject.optInt("images_extracted", 0),
                processingTime = jsonObject.optLong("processing_time", 0),
                extractionMethod = jsonObject.optString("extraction_method", "unknown"),
                languages = jsonObject.optString("languages", "").split(",").filter { it.isNotEmpty() },
                metadata = emptyMap(),
                warnings = jsonObject.optString("warnings", "").split(",").filter { it.isNotEmpty() },
                errors = jsonObject.optString("errors", "").split(",").filter { it.isNotEmpty() }
            )
            
            displayResults()
        }
    }
    
    private fun displayResults() {
        confidenceValue.text = String.format(Locale.getDefault(), "%.1f%%", processingResult.confidence * 100)
        pagesValue.text = processingResult.pagesProcessed.toString()
        tablesValue.text = processingResult.tablesExtracted.toString()
        imagesValue.text = processingResult.imagesExtracted.toString()
        methodValue.text = processingResult.extractionMethod
        timeValue.text = "${processingResult.processingTime} ms"
        textContent.setText(processingResult.text)
        
        // Set confidence color
        val color = when {
            processingResult.confidence >= 0.9 -> getColor(android.R.color.holo_green_dark)
            processingResult.confidence >= 0.7 -> getColor(android.R.color.holo_orange_dark)
            else -> getColor(android.R.color.holo_red_dark)
        }
        confidenceValue.setTextColor(color)
        
        // Show warnings if any
        if (processingResult.warnings.isNotEmpty()) {
            Toast.makeText(this, "Warnings: ${processingResult.warnings.size}", Toast.LENGTH_SHORT).show()
        }
    }
    
    private fun setupListeners() {
        copyButton.setOnClickListener {
            copyTextToClipboard()
        }
        
        saveButton.setOnClickListener {
            saveResultsToFile()
        }
    }
    
    private fun copyTextToClipboard() {
        val clipboard = getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
        val clip = ClipData.newPlainText("Extracted Text", processingResult.text)
        clipboard.setPrimaryClip(clip)
        Toast.makeText(this, "Text copied to clipboard", Toast.LENGTH_SHORT).show()
    }
    
    private fun saveResultsToFile() {
        try {
            val timestamp = SimpleDateFormat("yyyyMMdd_HHmmss", Locale.getDefault()).format(Date())
            val fileName = "pdf_extract_$timestamp.txt"
            
            val content = buildString {
                appendLine("=== PDF Extraction Results ===")
                appendLine("Date: ${SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.getDefault()).format(Date())}")
                appendLine("Confidence: ${String.format(Locale.getDefault(), "%.1f%%", processingResult.confidence * 100)}")
                appendLine("Pages Processed: ${processingResult.pagesProcessed}")
                appendLine("Tables Found: ${processingResult.tablesExtracted}")
                appendLine("Images Found: ${processingResult.imagesExtracted}")
                appendLine("Extraction Method: ${processingResult.extractionMethod}")
                appendLine("Processing Time: ${processingResult.processingTime} ms")
                appendLine("Languages: ${processingResult.languages.joinToString(", ")}")
                appendLine()
                appendLine("=== Extracted Text ===")
                appendLine(processingResult.text)
                appendLine()
                appendLine("=== Metadata ===")
                processingResult.metadata.forEach { (key, value) ->
                    appendLine("$key: $value")
                }
            }
            
            // Save to Downloads folder
            val downloadsDir = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS)
            val outputFile = File(downloadsDir, fileName)
            
            FileOutputStream(outputFile).use { fos ->
                fos.write(content.toByteArray())
            }
            
            Toast.makeText(this, "Results saved to: ${outputFile.absolutePath}", Toast.LENGTH_LONG).show()
        } catch (e: Exception) {
            Toast.makeText(this, "Error saving results: ${e.message}", Toast.LENGTH_LONG).show()
        }
    }
}
