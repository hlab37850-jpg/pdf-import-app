"""
PDF Import App - Main Entry Point
Kivy-based Android app with full PDF processing
"""

import os
import json
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.progressbar import ProgressBar
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.clock import Clock
import threading

# Import PDF engine
from engine.orchestrator import PDFImportOrchestrator


class PDFImportApp(App):
    """Main Kivy App"""
    
    def build(self):
        self.title = "PDF Import App"
        
        # Main layout
        self.main_layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # Title
        title = Label(
            text="PDF Import App",
            font_size=24,
            size_hint=(1, 0.1),
            bold=True
        )
        self.main_layout.add_widget(title)
        
        # Select PDF button
        self.select_btn = Button(
            text="Select PDF File",
            size_hint=(1, 0.15),
            background_color=(0.2, 0.6, 1, 1)
        )
        self.select_btn.bind(on_press=self.show_file_chooser)
        self.main_layout.add_widget(self.select_btn)
        
        # Process button
        self.process_btn = Button(
            text="Process PDF",
            size_hint=(1, 0.15),
            background_color=(0.2, 0.8, 0.4, 1),
            disabled=True
        )
        self.process_btn.bind(on_press=self.process_pdf)
        self.main_layout.add_widget(self.process_btn)
        
        # Progress bar
        self.progress = ProgressBar(max=100, size_hint=(1, 0.05))
        self.progress.value = 0
        self.main_layout.add_widget(self.progress)
        
        # Status label
        self.status_label = Label(
            text="No file selected",
            size_hint=(1, 0.1),
            font_size=14
        )
        self.main_layout.add_widget(self.status_label)
        
        # Results area
        self.results_scroll = ScrollView(size_hint=(1, 0.5))
        self.results_text = TextInput(
            text="",
            readonly=True,
            size_hint=(1, None),
            height=400,
            font_size=12,
            hint_text="Extracted text will appear here..."
        )
        self.results_scroll.add_widget(self.results_text)
        self.main_layout.add_widget(self.results_scroll)
        
        self.selected_pdf = None
        
        return self.main_layout
    
    def show_file_chooser(self, instance):
        """Show file chooser dialog"""
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        file_chooser = FileChooserListView(
            filters=["*.pdf", "*.PDF"],
            size_hint=(1, 0.8)
        )
        content.add_widget(file_chooser)
        
        select_btn = Button(
            text="Select",
            size_hint=(1, 0.1),
            background_color=(0.2, 0.6, 1, 1)
        )
        content.add_widget(select_btn)
        
        cancel_btn = Button(
            text="Cancel",
            size_hint=(1, 0.1),
            background_color=(0.8, 0.3, 0.3, 1)
        )
        content.add_widget(cancel_btn)
        
        popup = Popup(
            title="Select PDF File",
            content=content,
            size_hint=(0.9, 0.9)
        )
        
        def select_file(instance):
            if file_chooser.selection:
                self.selected_pdf = file_chooser.selection[0]
                self.status_label.text = f"Selected: {os.path.basename(self.selected_pdf)}"
                self.process_btn.disabled = False
                popup.dismiss()
        
        select_btn.bind(on_press=select_file)
        cancel_btn.bind(on_press=lambda x: popup.dismiss())
        
        popup.open()
    
    def process_pdf(self, instance):
        """Process selected PDF"""
        if not self.selected_pdf:
            return
        
        self.process_btn.disabled = True
        self.select_btn.disabled = True
        self.progress.value = 0
        self.status_label.text = "Processing PDF..."
        
        # Run processing in background thread
        thread = threading.Thread(target=self._process_pdf_thread)
        thread.daemon = True
        thread.start()
    
    def _process_pdf_thread(self):
        """Background PDF processing"""
        try:
            # Initialize orchestrator
            orchestrator = PDFImportOrchestrator()
            
            # Update progress
            def update_progress(dt):
                self.progress.value += 10
                if self.progress.value > 90:
                    self.progress.value = 90
            
            Clock.schedule_interval(update_progress, 0.5)
            
            # Process PDF
            result = orchestrator.process(self.selected_pdf)
            
            # Update UI
            def update_ui(dt):
                self.progress.value = 100
                self.status_label.text = f"Complete! Confidence: {result['confidence']:.1%}"
                
                # Display results
                display_text = f"""
=== PDF Processing Results ===

Confidence: {result['confidence']:.1%}
Pages Processed: {result['pages_processed']}
Tables Found: {result['tables_extracted']}
Images Found: {result['images_extracted']}
Method: {result['method']}

=== Extracted Text ===

{result['text'][:5000]}  # Show first 5000 characters
"""
                self.results_text.text = display_text
                
                self.process_btn.disabled = False
                self.select_btn.disabled = False
            
            Clock.schedule_once(update_ui, 0)
            
        except Exception as e:
            def show_error(dt):
                self.status_label.text = f"Error: {str(e)}"
                self.process_btn.disabled = False
                self.select_btn.disabled = False
            
            Clock.schedule_once(show_error, 0)


if __name__ == '__main__':
    PDFImportApp().run()
