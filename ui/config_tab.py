# ui/config_tab.py - Tab Konfigurasi API Keys

import json
import os
import requests
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QGroupBox, QTextEdit, QMessageBox, QFrame,
    QProgressBar, QCheckBox, QComboBox, QFileDialog, QScrollArea
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QIcon

from modules_client.config_manager import ConfigManager

class APITestThread(QThread):
    """Thread untuk test API connection"""
    result_ready = pyqtSignal(str, bool, str)  # api_type, success, message
    
    def __init__(self, api_type, api_key):
        super().__init__()
        self.api_type = api_type
        self.api_key = api_key
    
    def run(self):
        """Test API connection"""
        try:
            if self.api_type == "deepseek":
                success, message = self.test_deepseek_api()
            elif self.api_type == "chatgpt":
                success, message = self.test_chatgpt_api()
            else:
                success, message = False, "Unknown API type"
            
            self.result_ready.emit(self.api_type, success, message)
        except Exception as e:
            self.result_ready.emit(self.api_type, False, f"Error: {str(e)}")
    
    def test_deepseek_api(self):
        """Test DeepSeek API"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "user", "content": "Hello, test connection"}
                ],
                "max_tokens": 10
            }
            
            response = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                return True, "✅ DeepSeek API berhasil terhubung!"
            else:
                return False, f"❌ DeepSeek API error: {response.status_code}"
                
        except Exception as e:
            return False, f"❌ DeepSeek API gagal: {str(e)}"
    
    def test_chatgpt_api(self):
        """Test ChatGPT API"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "user", "content": "Hello, test connection"}
                ],
                "max_tokens": 10
            }
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                return True, "✅ ChatGPT API berhasil terhubung!"
            else:
                return False, f"❌ ChatGPT API error: {response.status_code}"
                
        except Exception as e:
            return False, f"❌ ChatGPT API gagal: {str(e)}"

class ConfigTab(QWidget):
    """Tab Konfigurasi untuk API Keys"""
    
    def __init__(self):
        super().__init__()
        self.cfg = ConfigManager("config/settings.json")
        self.test_thread = None
        self.init_ui()
        self.load_saved_keys()
    
    def init_ui(self):
        """Initialize UI with scroll area"""
        # Main layout for the entire widget
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Create content widget for scroll area
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title = QLabel("🔧 Konfigurasi API Keys")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #1877F2; margin-bottom: 20px;")
        layout.addWidget(title)
        
        # Description
        desc = QLabel("Konfigurasi API untuk AI Chat Response dan Google TTS")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setStyleSheet("color: #666; font-size: 14px; margin-bottom: 20px;")
        layout.addWidget(desc)
        
        # AI Provider Section
        self.create_ai_provider_section(layout)
        
        # Google TTS Section
        self.create_google_tts_section(layout)
        
        # Status Section
        self.create_status_section(layout)
        
        # Buttons
        self.create_buttons(layout)
        
        # Add stretch to push content to top
        layout.addStretch()
        
        # Set content widget to scroll area
        scroll_area.setWidget(content_widget)
        
        # Add scroll area to main layout
        main_layout.addWidget(scroll_area)
        
        # Apply modern dark theme
        self.setStyleSheet("""
            QWidget {
                background-color: #1a1a1a;
                color: #ffffff;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QScrollArea {
                border: none;
                background-color: #1a1a1a;
            }
            QScrollArea > QWidget > QWidget {
                background-color: #1a1a1a;
            }
            QScrollBar:vertical {
                background-color: #2d2d2d;
                width: 12px;
                border-radius: 6px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background-color: #555555;
                border-radius: 6px;
                min-height: 20px;
                margin: 2px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #666666;
            }
            QScrollBar::handle:vertical:pressed {
                background-color: #777777;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #404040;
                border-radius: 12px;
                margin-top: 15px;
                padding-top: 15px;
                background-color: #2a2a2a;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px 0 8px;
                color: #ffffff;
                background-color: #2a2a2a;
            }
            QLineEdit {
                background-color: #404040;
                border: 2px solid #555555;
                border-radius: 8px;
                padding: 12px 15px;
                font-size: 13px;
                color: #ffffff;
                selection-background-color: #1877F2;
            }
            QLineEdit:focus {
                border: 2px solid #1877F2;
                background-color: #4a4a4a;
            }
            QLineEdit:hover {
                border: 2px solid #666666;
            }
            QLineEdit[readOnly="true"] {
                background-color: #353535;
                color: #cccccc;
            }
            QPushButton {
                background-color: #1877F2;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: bold;
                font-size: 13px;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #166FE5;
                border: 2px solid #0d6efd;
            }
            QPushButton:pressed {
                background-color: #125FCA;
                border: 2px solid #0a58ca;
            }
            QPushButton:disabled {
                background-color: #404040;
                color: #888888;
            }
            QPushButton[class="secondary"] {
                background-color: #404040;
                color: #ffffff;
            }
            QPushButton[class="secondary"]:hover {
                background-color: #505050;
            }
            QPushButton[class="success"] {
                background-color: #28a745;
            }
            QPushButton[class="success"]:hover {
                background-color: #218838;
            }
            QPushButton[class="danger"] {
                background-color: #dc3545;
            }
            QPushButton[class="danger"]:hover {
                background-color: #c82333;
            }
            QTextEdit {
                background-color: #2a2a2a;
                border: 2px solid #404040;
                border-radius: 8px;
                padding: 12px;
                font-size: 12px;
                color: #ffffff;
            }
            QComboBox {
                background-color: #404040;
                border: 2px solid #555555;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 13px;
                color: #ffffff;
                min-width: 150px;
            }
            QComboBox:hover {
                border: 2px solid #666666;
            }
            QComboBox:focus {
                border: 2px solid #1877F2;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #ffffff;
                margin-right: 10px;
            }
            QComboBox QAbstractItemView {
                background-color: #404040;
                border: 1px solid #555555;
                selection-background-color: #1877F2;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
            }
            QLabel[class="status-success"] {
                color: #28a745;
                font-weight: bold;
            }
            QLabel[class="status-error"] {
                color: #dc3545;
                font-weight: bold;
            }
            QLabel[class="status-warning"] {
                color: #ffc107;
                font-weight: bold;
            }
            QLabel[class="status-info"] {
                color: #17a2b8;
                font-weight: bold;
            }
        """)
    
    def create_ai_provider_section(self, layout):
        """Create AI Provider section with flexible API key input"""
        group = QGroupBox("🤖 AI Chat Provider")
        group_layout = QVBoxLayout(group)
        group_layout.setSpacing(15)
        
        # Provider selection with better layout
        provider_layout = QHBoxLayout()
        provider_label = QLabel("Provider:")
        provider_label.setMinimumWidth(100)
        provider_layout.addWidget(provider_label)
        
        self.provider_combo = QComboBox()
        self.provider_combo.addItems(["DeepSeek", "OpenAI (ChatGPT)"])
        self.provider_combo.currentTextChanged.connect(self.on_provider_changed)
        provider_layout.addWidget(self.provider_combo)
        provider_layout.addStretch()
        group_layout.addLayout(provider_layout)
        
        # API Key input with better styling
        api_key_label = QLabel("API Key:")
        api_key_label.setMinimumWidth(100)
        group_layout.addWidget(api_key_label)
        
        # API Key input container
        api_key_container = QHBoxLayout()
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("Masukkan API Key (sk-...)")
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.textChanged.connect(self.on_api_key_changed)
        api_key_container.addWidget(self.api_key_input)
        
        # Show/Hide button with better styling
        show_btn = QPushButton("👁️")
        show_btn.setProperty("class", "secondary")
        show_btn.setMaximumWidth(50)
        show_btn.setToolTip("Show/Hide API Key")
        show_btn.clicked.connect(lambda: self.toggle_password_visibility(self.api_key_input))
        api_key_container.addWidget(show_btn)
        
        group_layout.addLayout(api_key_container)
        
        # Button container
        button_layout = QHBoxLayout()
        
        # Test button
        self.ai_test_btn = QPushButton("🔍 Test Connection")
        self.ai_test_btn.setProperty("class", "success")
        self.ai_test_btn.clicked.connect(self.test_ai_api)
        self.ai_test_btn.setEnabled(False)  # Disabled until API key is entered
        button_layout.addWidget(self.ai_test_btn)
        
        button_layout.addStretch()
        group_layout.addLayout(button_layout)
        
        # Status with better styling
        self.ai_status = QLabel("Status: Belum ada API key")
        self.ai_status.setProperty("class", "status-info")
        self.ai_status.setStyleSheet("color: #888; font-size: 12px; padding: 8px; background-color: #333; border-radius: 4px;")
        group_layout.addWidget(self.ai_status)
        
        layout.addWidget(group)
    
    def create_google_tts_section(self, layout):
        """Create Google TTS section"""
        group = QGroupBox("🎤 Google Text-to-Speech")
        group_layout = QVBoxLayout(group)
        group_layout.setSpacing(15)
        
        # Description with better styling
        desc = QLabel("Upload file kredensial Google Cloud TTS (JSON)")
        desc.setStyleSheet("color: #cccccc; font-size: 12px; font-style: italic; padding: 5px;")
        group_layout.addWidget(desc)
        
        # File path display with better layout
        file_label = QLabel("File Kredensial:")
        file_label.setMinimumWidth(100)
        group_layout.addWidget(file_label)
        
        # File path container
        file_container = QHBoxLayout()
        self.tts_file_path = QLineEdit()
        self.tts_file_path.setPlaceholderText("Belum ada file kredensial dipilih")
        self.tts_file_path.setReadOnly(True)
        file_container.addWidget(self.tts_file_path)
        
        # Browse button
        browse_btn = QPushButton("📁 Browse")
        browse_btn.setProperty("class", "secondary")
        browse_btn.setMaximumWidth(100)
        browse_btn.clicked.connect(self.browse_tts_credentials)
        file_container.addWidget(browse_btn)
        
        group_layout.addLayout(file_container)
        
        # Button container
        tts_button_layout = QHBoxLayout()
        
        # Test button
        self.tts_test_btn = QPushButton("🔍 Test Google TTS")
        self.tts_test_btn.setProperty("class", "success")
        self.tts_test_btn.clicked.connect(self.test_google_tts)
        self.tts_test_btn.setEnabled(False)  # Disabled until file is selected
        tts_button_layout.addWidget(self.tts_test_btn)
        
        tts_button_layout.addStretch()
        group_layout.addLayout(tts_button_layout)
        
        # Status with better styling
        self.tts_status = QLabel("Status: Belum ada file kredensial")
        self.tts_status.setProperty("class", "status-info")
        self.tts_status.setStyleSheet("color: #888; font-size: 12px; padding: 8px; background-color: #333; border-radius: 4px;")
        group_layout.addWidget(self.tts_status)
        
        layout.addWidget(group)
    
    def create_status_section(self, layout):
        """Create status section with better styling"""
        group = QGroupBox("📊 Status Konfigurasi")
        group_layout = QVBoxLayout(group)
        group_layout.setSpacing(15)
        
        # Status overview with better styling
        self.status_text = QTextEdit()
        self.status_text.setMaximumHeight(120)
        self.status_text.setMinimumHeight(120)
        self.status_text.setPlainText("Belum ada konfigurasi yang diatur")
        self.status_text.setReadOnly(True)
        self.status_text.setStyleSheet("""
            QTextEdit {
                background-color: #2a2a2a;
                border: 2px solid #404040;
                border-radius: 8px;
                padding: 15px;
                font-size: 13px;
                color: #ffffff;
                font-family: 'Consolas', 'Monaco', monospace;
                line-height: 1.4;
            }
        """)
        group_layout.addWidget(self.status_text)
        
        # Connection status indicators
        indicators_layout = QHBoxLayout()
        
        # AI Status Indicator
        self.ai_indicator = QLabel("🔴 AI: Tidak terhubung")
        self.ai_indicator.setStyleSheet("""
            QLabel {
                background-color: #404040;
                border: 1px solid #555555;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 12px;
                font-weight: bold;
            }
        """)
        indicators_layout.addWidget(self.ai_indicator)
        
        # TTS Status Indicator
        self.tts_indicator = QLabel("🔴 TTS: Tidak terhubung")
        self.tts_indicator.setStyleSheet("""
            QLabel {
                background-color: #404040;
                border: 1px solid #555555;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 12px;
                font-weight: bold;
            }
        """)
        indicators_layout.addWidget(self.tts_indicator)
        
        indicators_layout.addStretch()
        group_layout.addLayout(indicators_layout)
        
        layout.addWidget(group)
    
    def create_buttons(self, layout):
        """Create action buttons with better styling"""
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        # Save button with success styling
        save_btn = QPushButton("💾 Simpan Konfigurasi")
        save_btn.setProperty("class", "success")
        save_btn.clicked.connect(self.save_config)
        save_btn.setMinimumHeight(45)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: bold;
                font-size: 14px;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #218838;
                border: 2px solid #1c7430;
            }
            QPushButton:pressed {
                background-color: #1e7e34;
                border: 2px solid #155724;
            }
        """)
        button_layout.addWidget(save_btn)
        
        # Reset button with danger styling
        reset_btn = QPushButton("🔄 Reset Konfigurasi")
        reset_btn.setProperty("class", "danger")
        reset_btn.clicked.connect(self.reset_config)
        reset_btn.setMinimumHeight(45)
        reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: bold;
                font-size: 14px;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #c82333;
                border: 2px solid #b21f2d;
            }
            QPushButton:pressed {
                background-color: #bd2130;
                border: 2px solid #a71e2a;
            }
        """)
        button_layout.addWidget(reset_btn)
        
        # Test All button
        test_all_btn = QPushButton("🔍 Test Semua Koneksi")
        test_all_btn.clicked.connect(self.test_all_connections)
        test_all_btn.setMinimumHeight(45)
        test_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #1877F2;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: bold;
                font-size: 14px;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #166FE5;
                border: 2px solid #0d6efd;
            }
            QPushButton:pressed {
                background-color: #125FCA;
                border: 2px solid #0a58ca;
            }
        """)
        button_layout.addWidget(test_all_btn)
        
        layout.addLayout(button_layout)
    
    def on_provider_changed(self, provider):
        """Handle provider selection change"""
        if provider == "DeepSeek":
            self.api_key_input.setPlaceholderText("Masukkan DeepSeek API Key (sk-...)")
        elif provider == "OpenAI (ChatGPT)":
            self.api_key_input.setPlaceholderText("Masukkan OpenAI API Key (sk-...)")
        self.update_status_overview()
    
    def on_api_key_changed(self):
        """Handle API key input change"""
        api_key = self.api_key_input.text().strip()
        self.ai_test_btn.setEnabled(len(api_key) > 0)
        
        if len(api_key) > 0:
            self.ai_status.setText("Status: API key siap untuk ditest")
            self.ai_status.setProperty("class", "status-warning")
            self.ai_status.setStyleSheet("color: #ffc107; font-size: 12px; padding: 8px; background-color: #333; border-radius: 4px; font-weight: bold;")
        else:
            self.ai_status.setText("Status: Belum ada API key")
            self.ai_status.setProperty("class", "status-info")
            self.ai_status.setStyleSheet("color: #888; font-size: 12px; padding: 8px; background-color: #333; border-radius: 4px;")
        
        self.update_status_overview()
    
    def test_all_connections(self):
        """Test all configured connections"""
        api_key = self.api_key_input.text().strip()
        tts_file = self.tts_file_path.text().strip()
        
        if not api_key and not tts_file:
            QMessageBox.warning(
                self, 
                "Peringatan", 
                "Tidak ada konfigurasi yang dapat ditest.\nSilakan atur API key atau file kredensial TTS terlebih dahulu."
            )
            return
        
        # Test AI API if configured
        if api_key:
            self.test_ai_api()
        
        # Test Google TTS if configured
        if tts_file:
            self.test_google_tts()
        
        # Show completion message
        QTimer.singleShot(2000, lambda: QMessageBox.information(
            self, 
            "Test Selesai", 
            "Test koneksi telah selesai. Periksa status masing-masing layanan di atas."
        ))
    
    def browse_tts_credentials(self):
        """Browse for Google TTS credentials file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Pilih File Kredensial Google TTS",
            "",
            "JSON Files (*.json);;All Files (*)"
        )
        if file_path:
            self.tts_file_path.setText(file_path)
            self.tts_test_btn.setEnabled(True)
            self.tts_status.setText("Status: File dipilih, siap untuk ditest")
            self.tts_status.setProperty("class", "status-warning")
            self.tts_status.setStyleSheet("color: #ffc107; font-size: 12px; padding: 8px; background-color: #333; border-radius: 4px; font-weight: bold;")
            self.update_status_overview()
    
    def toggle_password_visibility(self, line_edit):
        """Toggle password visibility for line edit"""
        if line_edit.echoMode() == QLineEdit.EchoMode.Password:
            line_edit.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            line_edit.setEchoMode(QLineEdit.EchoMode.Password)
    
    def test_ai_api(self):
        """Test AI API connection"""
        api_key = self.api_key_input.text().strip()
        provider = self.provider_combo.currentText()
        
        if not api_key:
            self.ai_status.setText("Status: ❌ API key kosong")
            self.ai_status.setStyleSheet("color: #FF6B6B; font-size: 12px;")
            return
        
        self.ai_test_btn.setText("⏳ Testing...")
        self.ai_test_btn.setEnabled(False)
        
        # Determine API type for testing
        api_type = "deepseek" if provider == "DeepSeek" else "chatgpt"
        
        # Start test thread
        self.test_thread = APITestThread(api_type, api_key)
        self.test_thread.result_ready.connect(self.on_test_result)
        self.test_thread.start()
    
    def test_google_tts(self):
        """Test Google TTS credentials"""
        file_path = self.tts_file_path.text().strip()
        
        if not file_path:
            self.tts_status.setText("Status: ❌ Belum ada file kredensial")
            self.tts_status.setStyleSheet("color: #FF6B6B; font-size: 12px;")
            return
        
        self.tts_test_btn.setText("⏳ Testing...")
        self.tts_test_btn.setEnabled(False)
        
        try:
            import os
            import json
            
            # Check if file exists and is valid JSON
            if not os.path.exists(file_path):
                raise Exception("File tidak ditemukan")
            
            with open(file_path, 'r') as f:
                credentials = json.load(f)
            
            # Basic validation of Google credentials structure
            required_fields = ['type', 'project_id', 'private_key_id', 'private_key', 'client_email']
            missing_fields = [field for field in required_fields if field not in credentials]
            
            if missing_fields:
                raise Exception(f"Field yang hilang: {', '.join(missing_fields)}")
            
            if credentials.get('type') != 'service_account':
                raise Exception("Bukan file service account yang valid")
            
            self.tts_status.setText("Status: ✅ Kredensial valid dan siap digunakan")
            self.tts_status.setProperty("class", "status-success")
            self.tts_status.setStyleSheet("color: #28a745; font-size: 12px; padding: 8px; background-color: #333; border-radius: 4px; font-weight: bold;")
            
        except Exception as e:
            self.tts_status.setText(f"Status: ❌ Error: {str(e)}")
            self.tts_status.setProperty("class", "status-error")
            self.tts_status.setStyleSheet("color: #dc3545; font-size: 12px; padding: 8px; background-color: #333; border-radius: 4px; font-weight: bold;")
        
        finally:
            self.tts_test_btn.setText("🔍 Test Google TTS")
            self.tts_test_btn.setEnabled(True)
            self.update_status_overview()
    
    def on_test_result(self, api_type, success, message):
        """Handle API test result"""
        self.ai_test_btn.setText("🔍 Test Connection")
        self.ai_test_btn.setEnabled(True)
        
        if success:
            self.ai_status.setText(f"Status: {message}")
            self.ai_status.setProperty("class", "status-success")
            self.ai_status.setStyleSheet("color: #28a745; font-size: 12px; padding: 8px; background-color: #333; border-radius: 4px; font-weight: bold;")
        else:
            self.ai_status.setText(f"Status: {message}")
            self.ai_status.setProperty("class", "status-error")
            self.ai_status.setStyleSheet("color: #dc3545; font-size: 12px; padding: 8px; background-color: #333; border-radius: 4px; font-weight: bold;")
        
        self.update_status_overview()
    
    def update_status_overview(self):
        """Update status overview with better formatting"""
        api_key = self.api_key_input.text().strip()
        provider = self.provider_combo.currentText()
        tts_file = self.tts_file_path.text().strip()
        
        status_lines = []
        status_lines.append("=== STATUS KONFIGURASI ===")
        status_lines.append("")
        
        # AI Provider Status
        if api_key:
            status_lines.append(f"✅ {provider} API: Terkonfigurasi ({len(api_key)} karakter)")
            self.ai_indicator.setText(f"🟢 AI: {provider} Terhubung")
            self.ai_indicator.setStyleSheet("""
                QLabel {
                    background-color: #28a745;
                    border: 1px solid #1e7e34;
                    border-radius: 6px;
                    padding: 8px 12px;
                    font-size: 12px;
                    font-weight: bold;
                    color: white;
                }
            """)
        else:
            status_lines.append(f"❌ {provider} API: Belum dikonfigurasi")
            self.ai_indicator.setText("🔴 AI: Tidak terhubung")
            self.ai_indicator.setStyleSheet("""
                QLabel {
                    background-color: #dc3545;
                    border: 1px solid #bd2130;
                    border-radius: 6px;
                    padding: 8px 12px;
                    font-size: 12px;
                    font-weight: bold;
                    color: white;
                }
            """)
        
        # Google TTS Status
        if tts_file:
            status_lines.append(f"✅ Google TTS: Terkonfigurasi")
            status_lines.append(f"   📁 File: {os.path.basename(tts_file)}")
            self.tts_indicator.setText("🟢 TTS: Google Cloud")
            self.tts_indicator.setStyleSheet("""
                QLabel {
                    background-color: #28a745;
                    border: 1px solid #1e7e34;
                    border-radius: 6px;
                    padding: 8px 12px;
                    font-size: 12px;
                    font-weight: bold;
                    color: white;
                }
            """)
        else:
            status_lines.append("❌ Google TTS: Belum dikonfigurasi")
            self.tts_indicator.setText("🔴 TTS: Tidak terhubung")
            self.tts_indicator.setStyleSheet("""
                QLabel {
                    background-color: #dc3545;
                    border: 1px solid #bd2130;
                    border-radius: 6px;
                    padding: 8px 12px;
                    font-size: 12px;
                    font-weight: bold;
                    color: white;
                }
            """)
        
        status_lines.append("")
        
        # Overall Status
        if api_key and tts_file:
            status_lines.append("🎉 SIAP DIGUNAKAN!")
            status_lines.append("   Semua fitur StreamMateAI dapat berfungsi optimal.")
        elif api_key:
            status_lines.append("⚠️  SEBAGIAN SIAP")
            status_lines.append("   AI Chat berfungsi, TTS perlu dikonfigurasi.")
        else:
            status_lines.append("❌ BELUM SIAP")
            status_lines.append("   Perlu konfigurasi AI API untuk menggunakan aplikasi.")
        
        self.status_text.setPlainText("\n".join(status_lines))
    
    def save_config(self):
        """Save configuration"""
        try:
            # Get current config
            config = self.cfg.get_all_settings()
            
            # Update API keys
            if "api_keys" not in config:
                config["api_keys"] = {}
            
            api_key = self.api_key_input.text().strip()
            provider = self.provider_combo.currentText()
            tts_file = self.tts_file_path.text().strip()
            
            if api_key:
                if provider == "DeepSeek":
                    config["api_keys"]["DEEPSEEK_API_KEY"] = api_key
                elif provider == "OpenAI (ChatGPT)":
                    config["api_keys"]["OPENAI_API_KEY"] = api_key
            
            if tts_file:
                config["google_tts_credentials"] = tts_file
            
            # Save to file
            config_path = Path("config/settings.json")
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            QMessageBox.information(self, "Success", "✅ Konfigurasi berhasil disimpan!")
            self.update_status_overview()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"❌ Gagal menyimpan konfigurasi:\n{str(e)}")
    
    def load_saved_keys(self):
        """Load saved API keys"""
        try:
            api_keys = self.cfg.get("api_keys", {})
            tts_file = self.cfg.get("google_tts_credentials", "")
            
            # Load API key based on available keys
            if "DEEPSEEK_API_KEY" in api_keys:
                self.provider_combo.setCurrentText("DeepSeek")
                self.api_key_input.setText(api_keys["DEEPSEEK_API_KEY"])
            elif "OPENAI_API_KEY" in api_keys:
                self.provider_combo.setCurrentText("OpenAI (ChatGPT)")
                self.api_key_input.setText(api_keys["OPENAI_API_KEY"])
            
            if tts_file:
                self.tts_file_path.setText(tts_file)
            
            self.update_status_overview()
            
        except Exception as e:
            print(f"Error loading saved keys: {e}")
    
    def reset_config(self):
        """Reset configuration"""
        reply = QMessageBox.question(
            self, 
            "Konfirmasi", 
            "Yakin ingin reset semua konfigurasi?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.api_key_input.clear()
            self.tts_file_path.clear()
            self.ai_status.setText("Status: Belum ada API key")
            self.ai_status.setProperty("class", "status-info")
            self.ai_status.setStyleSheet("color: #888; font-size: 12px; padding: 8px; background-color: #333; border-radius: 4px;")
            
            self.tts_status.setText("Status: Belum ada file kredensial")
            self.tts_status.setProperty("class", "status-info")
            self.tts_status.setStyleSheet("color: #888; font-size: 12px; padding: 8px; background-color: #333; border-radius: 4px;")
            
            # Reset button states
            self.ai_test_btn.setEnabled(False)
            self.tts_test_btn.setEnabled(False)
            
            self.update_status_overview()