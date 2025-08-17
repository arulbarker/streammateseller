#!/usr/bin/env python3
"""
StreamMate AI - Live Streaming Automation
Main Entry Point - Fixed Version for Windows Encoding
"""

import sys
import os
import multiprocessing

# CRITICAL FIX: Set Windows Console Encoding to UTF-8 to prevent UnicodeEncodeError
if sys.platform == "win32":
    import codecs
    # Force UTF-8 encoding for stdout and stderr to handle emoji/Unicode
    if hasattr(sys.stdout, 'reconfigure'):
        try:
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
        except:
            # Fallback: Wrap stdout/stderr with UTF-8 encoder - FIX for EXE
            try:
                stdout_buffer = sys.stdout.detach()
                stderr_buffer = sys.stderr.detach()
                
                # Check if detach() returned valid buffers (not None)
                if stdout_buffer is not None:
                    sys.stdout = codecs.getwriter('utf-8')(stdout_buffer, errors='replace')
                if stderr_buffer is not None:
                    sys.stderr = codecs.getwriter('utf-8')(stderr_buffer, errors='replace')
            except (AttributeError, OSError):
                # In frozen executable, detach might not work - skip encoding fix
                print("[WARNING] Cannot reconfigure stdout/stderr encoding in executable mode")
                pass
    else:
        # For older Python versions - with EXE compatibility check
        try:
            stdout_buffer = sys.stdout.detach()
            stderr_buffer = sys.stderr.detach()
            
            # Check if detach() returned valid buffers (not None)
            if stdout_buffer is not None:
                sys.stdout = codecs.getwriter('utf-8')(stdout_buffer, errors='replace')
            if stderr_buffer is not None:
                sys.stderr = codecs.getwriter('utf-8')(stderr_buffer, errors='replace')
        except (AttributeError, OSError):
            # In frozen executable, detach might not work - skip encoding fix
            print("[WARNING] Cannot reconfigure stdout/stderr encoding in executable mode")
            pass

import traceback
import json
import time
import importlib.util
import threading
from datetime import datetime
from pathlib import Path
from logging.handlers import RotatingFileHandler
import logging

# ========== CRITICAL: HIGH DPI SETUP SEBELUM IMPORT PYQT6 ==========
# Ini HARUS dipanggil sebelum QGuiApplication atau QApplication dibuat
os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
os.environ["QT_SCALE_FACTOR_ROUNDING_POLICY"] = "PassThrough"
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

# Root project directory PERTAMA
ROOT = os.path.dirname(os.path.abspath(__file__))

# Setup logging system SEBELUM import lainnya
LOG_DIR = Path(ROOT) / "logs"
LOG_DIR.mkdir(exist_ok=True)
SYSTEM_LOG = LOG_DIR / "system.log"

# Configure logging dengan format yang lebih informatif
logger = logging.getLogger('StreamMate')
logger.setLevel(logging.INFO)

# File handler dengan rotation
file_handler = RotatingFileHandler(
    SYSTEM_LOG, 
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5,
    encoding='utf-8'
)
file_handler.setLevel(logging.INFO)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.WARNING)

# Format log yang lebih detail
formatter = logging.Formatter(
    '[%(asctime)s] [%(name)s] [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# ========== LOG STARTUP INFO ==========
logger.info("=" * 60)
logger.info("StreamMate AI Starting - Version 1.0.9")
logger.info(f"Python {sys.version}")
logger.info(f"Root directory: {ROOT}")
logger.info(f"Platform: {sys.platform}")
logger.info("=" * 60)

# ========== FORCE PRODUCTION MODE ==========
def detect_application_mode():
    """Force production mode - no development mode allowed"""
    print("[PROD] MODE: Production (FORCED)")
    return "production"

# Panggil detection
APP_MODE = detect_application_mode()
logger.info(f"Application mode: {APP_MODE}")

# Export ke environment untuk module lain
os.environ["STREAMMATE_APP_MODE"] = APP_MODE

# ========== SETUP PYTHON PATH ==========
# Add project paths to Python path SEBELUM import modules
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "modules_client"))
sys.path.insert(0, os.path.join(ROOT, "modules_server"))
sys.path.insert(0, os.path.join(ROOT, "ui"))
sys.path.insert(0, os.path.join(ROOT, "listeners"))

logger.info(f"Python path updated with {len(sys.path)} entries")

# ========== SEKARANG BARU IMPORT PYQT6 ==========
try:
    from PyQt6.QtCore import Qt, QTimer
    from PyQt6.QtGui import QGuiApplication, QIcon, QPixmap
    from PyQt6.QtWidgets import QApplication, QMessageBox, QSplashScreen
    logger.info("PyQt6 imported successfully")
except ImportError as e:
    print(f"CRITICAL: PyQt6 not found: {e}")
    print("Please install PyQt6: pip install PyQt6")
    sys.exit(1)

# ========== GLOBAL EXCEPTION HANDLER ==========
def handle_exception(exc_type, exc_value, exc_traceback):
    """Enhanced global exception handler dengan debug logging"""
    # Skip keyboard interrupt
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    # Format error message dengan full traceback
    error_msg = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    
    # Enhanced logging dengan lebih banyak detail
    logger.critical(f"[FORCE-CLOSE-DEBUG] Uncaught Exception: {exc_type.__name__}: {exc_value}")
    logger.critical(f"[FORCE-CLOSE-DEBUG] Traceback:\n{error_msg}")
    
    # Print ke console untuk debugging real-time
    print(f"\n[FORCE-CLOSE-DEBUG] ========== CRITICAL ERROR ==========")
    print(f"[FORCE-CLOSE-DEBUG] Exception Type: {exc_type.__name__}")
    print(f"[FORCE-CLOSE-DEBUG] Exception Value: {exc_value}")
    print(f"[FORCE-CLOSE-DEBUG] Traceback:")
    print(error_msg)
    print(f"[FORCE-CLOSE-DEBUG] =====================================\n")
    
    # Save error to temp file untuk debugging
    error_log_path = Path(ROOT) / "temp" / "error_log.txt"
    error_log_path.parent.mkdir(exist_ok=True)
    
    try:
        with open(error_log_path, "a", encoding="utf-8") as f:
            f.write(f"\n[{datetime.now().isoformat()}] FORCE-CLOSE-DEBUG:\n")
            f.write(f"Exception Type: {exc_type.__name__}\n")
            f.write(f"Exception Value: {exc_value}\n")
            f.write(f"Traceback:\n{error_msg}")
            f.write("\n" + "="*80 + "\n")
        logger.info(f"[FORCE-CLOSE-DEBUG] Error details saved to: {error_log_path}")
        print(f"[FORCE-CLOSE-DEBUG] Error details saved to: {error_log_path}")
    except Exception as log_error:
        logger.error(f"[FORCE-CLOSE-DEBUG] Failed to write error log: {log_error}")
        print(f"[FORCE-CLOSE-DEBUG] Failed to write error log: {log_error}")
    
    # Enhanced error handling - try to keep app alive for non-critical errors
    critical_errors = [
        'SystemError', 'MemoryError', 'KeyboardInterrupt', 
        'SystemExit', 'GeneratorExit', 'RuntimeError'
    ]
    
    error_name = exc_type.__name__
    is_critical = error_name in critical_errors
    
    print(f"[FORCE-CLOSE-DEBUG] Error classification: {'CRITICAL' if is_critical else 'NON-CRITICAL'}")
    
    # Show error dialog jika QApplication sudah ada
    try:
        if QApplication.instance():
            if is_critical:
                print(f"[FORCE-CLOSE-DEBUG] Showing critical error dialog and forcing exit")
                reply = QMessageBox.critical(
                    None, 
                    "StreamMate AI - Critical Error",
                    f"Application encountered a critical error and must close:\n\n"
                    f"{exc_type.__name__}: {exc_value}\n\n"
                    f"Error details saved to: {error_log_path}\n\n"
                    f"Click OK to exit application.",
                    QMessageBox.StandardButton.Ok
                )
                # Force exit for critical errors
                QApplication.instance().quit()
            else:
                print(f"[FORCE-CLOSE-DEBUG] Showing recoverable error dialog")
                reply = QMessageBox.warning(
                    None, 
                    "StreamMate AI - Error Recovered",
                    f"Application encountered an error but will continue:\n\n"
                    f"{exc_type.__name__}: {exc_value}\n\n"
                    f"Error details saved to: {error_log_path}\n\n"
                    f"If problems persist, please restart the application.",
                    QMessageBox.StandardButton.Ok
                )
                # Try to continue for non-critical errors
                print(f"[FORCE-CLOSE-DEBUG] Attempting to continue after non-critical error")
                return
    except Exception as dialog_error:
        # If even the error dialog fails, log it and exit gracefully
        logger.error(f"[FORCE-CLOSE-DEBUG] Failed to show error dialog: {dialog_error}")
        print(f"[FORCE-CLOSE-DEBUG] Failed to show error dialog: {dialog_error}")
        if is_critical:
            print(f"[FORCE-CLOSE-DEBUG] Forcing exit due to critical error")
            sys.exit(1)

# Install global exception handler
sys.excepthook = handle_exception

def check_dependencies():
    """Check critical dependencies sebelum aplikasi dimulai"""
    logger.info("Checking critical dependencies...")
    
    required_modules = {
        'PyQt6': 'pip install PyQt6',
        'requests': 'pip install requests',
        'sounddevice': 'pip install sounddevice',
        'soundfile': 'pip install soundfile',
        'keyboard': 'pip install keyboard',
        'pathlib': 'Built-in module'
    }
    
    missing_modules = []
    
    for module, install_cmd in required_modules.items():
        try:
            if module == 'PyQt6':
                # PyQt6 sudah diimport di atas
                continue
            else:
                __import__(module)
            logger.debug(f"[OK] {module} - OK")
        except ImportError:
            missing_modules.append((module, install_cmd))
            logger.error(f"[MISSING] {module} - MISSING")
    
    if missing_modules:
        error_msg = "Missing required dependencies:\n\n"
        for module, cmd in missing_modules:
            error_msg += f"- {module}: {cmd}\n"
        
        logger.error("Critical dependencies missing!")
        print(error_msg)
        return False
    
    logger.info("All critical dependencies OK")
    return True

def initialize_directories():
    """Initialize required directories dengan error handling"""
    logger.info("Initializing directory structure...")
    
    required_dirs = [
        "temp", "logs", "config", "knowledge", 
        "knowledge_bases", "avatars", "assets",
        "temp/cache", "resources"
    ]
    
    for directory in required_dirs:
        dir_path = Path(ROOT) / directory
        try:
            dir_path.mkdir(parents=True, exist_ok=True)
            logger.debug(f"[OK] Directory created/verified: {directory}")
        except Exception as e:
            logger.error(f"[ERROR] Failed to create directory {directory}: {e}")
            return False
    
    logger.info("Directory structure initialized successfully")
    return True

def main():
    """Main application entry point"""
    logger.info("Starting main application...")
    
    # Check dependencies
    if not check_dependencies():
        logger.critical("Critical dependencies missing, exiting...")
        return 1
    
    # Initialize directories
    if not initialize_directories():
        logger.critical("Failed to initialize directories, exiting...")
        return 1
    
    print("[SUCCESS] StreamMate AI main application initialized successfully")
    print(f"[INFO] Mode: {APP_MODE}")
    print(f"[INFO] Root directory: {ROOT}")
    
    # LAUNCH GUI APPLICATION
    try:
        print("[GUI] Launching StreamMate AI GUI...")
        
        # Create QApplication
        app = QApplication(sys.argv)
        
        # Set application properties
        app.setApplicationName("StreamMate AI")
        app.setApplicationVersion("1.0.9")
        app.setOrganizationName("StreamMate AI")
        app.setOrganizationDomain("streammate-ai.com")
        
        # Apply dark theme
        app.setStyle('Fusion')
        
        # ⚡ LOADING INDICATOR: Simple console-based loading for now
        print("[LOADING] StreamMate AI is starting up...")
        splash = None  # Disable splash screen to prevent segfault
        
        # Import and create main window
        sys.path.insert(0, os.path.join(ROOT, "ui"))
        
        # Console loading progress
        print("[LOADING] Setting up UI components...")
        
        # Fix relative imports for frozen executable
        import importlib.util
        
        # Load main_window module with proper path handling
        main_window_path = os.path.join(ROOT, "ui", "main_window.py")
        
        print("[LOADING] Loading main window...")
        
        # Check if running from frozen executable
        if getattr(sys, 'frozen', False):
            # In frozen mode, try direct import
            try:
                from ui.main_window import MainWindow
                print("[GUI] Imported MainWindow from ui.main_window")
            except ImportError:
                # Fallback: manual module loading
                spec = importlib.util.spec_from_file_location("main_window", main_window_path)
                main_window_module = importlib.util.module_from_spec(spec)
                sys.modules["main_window"] = main_window_module
                spec.loader.exec_module(main_window_module)
                MainWindow = main_window_module.MainWindow
                print("[GUI] Loaded MainWindow via importlib")
        else:
            # Development mode
            try:
                # Try standard import first
                from ui.main_window import MainWindow
                print("[GUI] Imported MainWindow from ui.main_window (development mode)")
            except ImportError:
                # Fallback: manual module loading untuk development mode
                spec = importlib.util.spec_from_file_location("main_window", main_window_path)
                main_window_module = importlib.util.module_from_spec(spec)
                sys.modules["main_window"] = main_window_module
                spec.loader.exec_module(main_window_module)
                MainWindow = main_window_module.MainWindow
                print("[GUI] Loaded MainWindow via importlib (development mode fallback)")
        
        # Console loading progress
        print("[LOADING] Initializing features...")
        
        # Create main window
        main_window = MainWindow()
        
        print("[LOADING] Finalizing startup...")
        
        main_window.show()
        
        print("[LOADING] Ready!")
        
        print("[GUI] StreamMate AI GUI launched successfully")
        logger.info("GUI application started")
        
        # Start event loop
        exit_code = app.exec()
        
        print("[GUI] StreamMate AI GUI closed")
        logger.info("GUI application closed")
        
        return exit_code
        
    except Exception as e:
        error_msg = f"Failed to launch GUI: {e}"
        print(f"[ERROR] {error_msg}")
        logger.error(error_msg)
        
        # Show error in message box if possible
        try:
            QMessageBox.critical(None, "StreamMate AI Error", error_msg)
        except:
            pass
            
        return 1

if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()