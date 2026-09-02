package com.pdfimport.app

import com.chaquo.python.PyObject
import com.chaquo.python.Python
import org.json.JSONObject

object PythonPDFProcessor {
    
    fun processPDF(pdfPath: String): PDFProcessingResult {
        val py = Python.getInstance()
        val module = py.getModule("main")
        
        val result = module.callAttr("process_pdf", pdfPath)
        
        return parseResult(result)
    }
    
    private fun parseResult(pyObject: PyObject): PDFProcessingResult {
        val jsonString = pyObject.callAttr("to_json").toString()
        val jsonObject = JSONObject(jsonString)
        
        return PDFProcessingResult(
            text = jsonObject.optString("text", ""),
            confidence = jsonObject.optDouble("confidence", 0.0),
            pagesProcessed = jsonObject.optInt("pages_processed", 0),
            tablesExtracted = jsonObject.optInt("tables_extracted", 0),
            imagesExtracted = jsonObject.optInt("images_extracted", 0),
            processingTime = jsonObject.optLong("processing_time", 0),
            extractionMethod = jsonObject.optString("extraction_method", "unknown"),
            languages = jsonObject.optJSONArray("languages")?.let { array ->
                (0 until array.length()).map { array.getString(it) }
            } ?: emptyList(),
            metadata = jsonObject.optJSONObject("metadata")?.let { obj ->
                val map = mutableMapOf<String, String>()
                obj.keys().forEach { key ->
                    map[key] = obj.optString(key, "")
                }
                map
            } ?: emptyMap(),
            warnings = jsonObject.optJSONArray("warnings")?.let { array ->
                (0 until array.length()).map { array.getString(it) }
            } ?: emptyList(),
            errors = jsonObject.optJSONArray("errors")?.let { array ->
                (0 until array.length()).map { array.getString(it) }
            } ?: emptyList()
        )
    }
}

data class PDFProcessingResult(
    val text: String,
    val confidence: Double,
    val pagesProcessed: Int,
    val tablesExtracted: Int,
    val imagesExtracted: Int,
    val processingTime: Long,
    val extractionMethod: String,
    val languages: List<String>,
    val metadata: Map<String, String>,
    val warnings: List<String>,
    val errors: List<String>
) {
    fun toJson(): String {
        return JSONObject().apply {
            put("text", text)
            put("confidence", confidence)
            put("pages_processed", pagesProcessed)
            put("tables_extracted", tablesExtracted)
            put("images_extracted", imagesExtracted)
            put("processing_time", processingTime)
            put("extraction_method", extractionMethod)
            put("languages", languages.joinToString(","))
            put("metadata", JSONObject(metadata))
            put("warnings", warnings.joinToString(","))
            put("errors", errors.joinToString(","))
        }.toString()
    }
}
