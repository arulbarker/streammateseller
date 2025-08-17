# ui/main_window.py - BASIC MODE ONLY VERSION
import sys
import os
import datetime
import json 
import logging
from pathlib import Path
from datetime import datetime, timedelta
import pytz
import subprocess
import time

# Setup logger
logger = logging.getLogger('StreamMate')
from datetime import timezone

# ✅ SUPABASE-ONLY MODE DETECTION
def _is_supabase_only_mode() -> bool:
    """Check if system should use Supabase-only mode (no VPS calls)"""
    try:
        supabase_config = Path("config/supabase_config.json")
        if supabase_config.exists():
            return True
        return False
    except:
        return False

def safe_attr_check(obj, attr_name):
    """Safely check if an object has an attribute"""
    try:
        return hasattr(obj, attr_name)
    except Exception:
        return False

# Import PyQt6 components
from PyQt6.QtGui import QGuiApplication, QIcon
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QStackedWidget, QTabWidget, QMessageBox,
    QLabel, QStatusBar, QWidget, QVBoxLayout, QPushButton, QSizePolicy, QInputDialog
)

# Setup project root
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Skema warna Facebook Theme - DARK MODE
FB_COLORS = {
    "primary": "#1877F2",
    "secondary": "#4267B2", 
    "light_bg": "#18191A",
    "dark_bg": "#0F1419",
    "text_primary": "#FFFFFF",
    "text_secondary": "#B0B3B8",
    "button_primary": "#1877F2",
    "button_secondary": "#3A3B3C",
    "success": "#42B72A",
    "warning": "#F5B800",
    "error": "#FA383E",
}

# Global dark theme styles
DARK_THEME = """
    QMainWindow, QWidget {
        background-color: #18191A;
        color: #FFFFFF;
    }
    
    QTabWidget::pane {
        border: 1px solid #3A3B3C;
        background-color: #18191A;
    }
    
    QTabBar::tab {
        background-color: #242526;
        color: #B0B3B8;
        padding: 8px 12px;
        border: none;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
    }
    
    QTabBar::tab:selected {
        background-color: #3A3B3C;
        color: #FFFFFF;
    }
    
    QTabBar::tab:hover:!selected {
        background-color: #2C2D2E;
    }
    
    QStatusBar {
        background-color: #242526;
        color: #B0B3B8;
    }
    
    QLineEdit, QTextEdit {
        background-color: #3A3B3C;
        color: #FFFFFF;
        border: 1px solid #4E4F50;
        border-radius: 4px;
        padding: 4px;
    }
    
    QLineEdit:focus, QTextEdit:focus {
        border: 1px solid #1877F2;
    }
    
    QComboBox {
        background-color: #3A3B3C;
        color: #FFFFFF;
        border: 1px solid #4E4F50;
        border-radius: 4px;
        padding: 4px;
    }
    
    QCheckBox {
        color: #FFFFFF;
    }
    
    QMessageBox {
        background-color: #18191A;
    }
    
    QMessageBox QLabel {
        color: #FFFFFF;
    }
    
    QProgressBar {
        background-color: #3A3B3C;
        border: none;
        border-radius: 4px;
        text-align: center;
        color: #FFFFFF;
    }
    
    QProgressBar::chunk {
        background-color: #1877F2;
        border-radius: 4px;
    }
"""

# Import ConfigManager
from modules_client.config_manager import ConfigManager

# Import Supabase client
from modules_client.supabase_client import SupabaseClient

# PRODUCTION MODE: SUPABASE-ONLY VALIDATION
import sys

def _is_production_mode():
    """Check if running in production (EXE) mode"""
    return getattr(sys, 'frozen', False)

# Import License validator dengan fallback untuk Supabase
try:
    from modules_client.supabase_client import SupabaseClient
    has_supabase_client = True
except ImportError:
    has_supabase_client = False
    
    class SupabaseClient:
        def __init__(self):
            pass
            
        def validate_license(self, email, hardware_id=None):
            """SUPABASE MODE: Supabase-only validation"""
            return {
                "is_valid": False,
                "tier": "none",
                "message": "Supabase validation required",
                "source": "supabase_only",
                "hours_credit": 0.0
            }

# Import UI tabs yang tersedia untuk Basic mode
try:
    from ui.login_tab import LoginTab
except ImportError:
    from login_tab import LoginTab

try:
    from ui.subscription_tab import SubscriptionTab
except ImportError:
    from subscription_tab import SubscriptionTab

# SystemLogTab import - DISABLED for end users (Developer tool only)
# try:
#     from ui.system_log_tab import SystemLogTab
# except ImportError:
#     from system_log_tab import SystemLogTab

try:
    from ui.profile_tab import ProfileTab
except ImportError:
    from profile_tab import ProfileTab

# Import cohost tab untuk Basic mode
try:
    from ui.cohost_tab_basic import CohostTabBasic
    COHOST_AVAILABLE = True
    print("[INFO] CohostTabBasic imported successfully")
except ImportError:
    try:
        from cohost_tab_basic import CohostTabBasic
        COHOST_AVAILABLE = True
        print("[INFO] CohostTabBasic imported successfully (fallback)")
    except ImportError:
        COHOST_AVAILABLE = False
        print("[WARNING] CohostTabBasic not available")

# Import overlay tab jika tersedia
try:
    from ui.overlay_tab import OverlayTab
    OVERLAY_AVAILABLE = True
except ImportError:
    try:
        from overlay_tab import OverlayTab
        OVERLAY_AVAILABLE = True
    except ImportError:
        OVERLAY_AVAILABLE = False
        print("[WARNING] OverlayTab not available")

# Import trakteer tab jika tersedia
try:
    from ui.trakteer_tab import TrakteerTab
    TRAKTEER_AVAILABLE = True
except ImportError:
    try:
        from trakteer_tab import TrakteerTab
        TRAKTEER_AVAILABLE = True
    except ImportError:
        TRAKTEER_AVAILABLE = False
        print("[WARNING] TrakteerTab not available")

# Import reply log tab jika tersedia
try:
    from ui.reply_log_tab import ReplyLogTab
    REPLY_LOG_AVAILABLE = True
except ImportError:
    try:
        from reply_log_tab import ReplyLogTab
        REPLY_LOG_AVAILABLE = True
    except ImportError:
        REPLY_LOG_AVAILABLE = False
        print("[WARNING] ReplyLogTab not available")

# Import tutorial tab jika tersedia
try:
    from ui.tutorial_tab import TutorialTab
    TUTORIAL_AVAILABLE = True
except ImportError:
    try:
        from tutorial_tab import TutorialTab
        TUTORIAL_AVAILABLE = True
    except ImportError:
        TUTORIAL_AVAILABLE = False
        print("[WARNING] TutorialTab not available")

# Import CoHost Seller tab
try:
    from ui.cohost_seller_tab import CohostSellerTab
    COHOST_SELLER_AVAILABLE = True
except ImportError:
    try:
        from cohost_seller_tab import CohostSellerTab
        COHOST_SELLER_AVAILABLE = True
    except ImportError:
        COHOST_SELLER_AVAILABLE = False
        print("[WARNING] CohostSellerTab not available")

# Import CoHost Pro tab
try:
    print("[DEBUG] Attempting to import CohostTabPro from ui.cohost_tab_pro...")
    from ui.cohost_tab_pro import CohostTabPro
    COHOST_PRO_AVAILABLE = True
    print("[DEBUG] CohostTabPro imported successfully from ui.cohost_tab_pro")
except Exception as e:
    print(f"[ERROR] Failed to import CohostTabPro from ui.cohost_tab_pro: {e}")
    import traceback
    traceback.print_exc()
    COHOST_PRO_AVAILABLE = False
    print("[WARNING] CohostTabPro not available")

# Import Viewers tab
try:
    from ui.viewers_tab import ViewersTab
    VIEWERS_AVAILABLE = True
except ImportError:
    try:
        from viewers_tab import ViewersTab
        VIEWERS_AVAILABLE = True
    except ImportError:
        VIEWERS_AVAILABLE = False
        print("[WARNING] ViewersTab not available")

# Import Virtual Mic tab
try:
    from ui.virtual_mic_tab import VirtualMicTab
    VIRTUAL_MIC_AVAILABLE = True
except ImportError:
    try:
        from virtual_mic_tab import VirtualMicTab
        VIRTUAL_MIC_AVAILABLE = True
    except ImportError:
        VIRTUAL_MIC_AVAILABLE = False
        print("[WARNING] VirtualMicTab not available")

# Import Translate Pro tab
try:
    from ui.translate_tab_pro import TranslateTabPro
    TRANSLATE_PRO_AVAILABLE = True
except ImportError:
    try:
        from translate_tab_pro import TranslateTabPro
        TRANSLATE_PRO_AVAILABLE = True
    except ImportError:
        TRANSLATE_PRO_AVAILABLE = False
        print("[WARNING] TranslateTabPro not available")

# Import Credit Wallet tab
try:
    from ui.credit_wallet_tab import CreditWalletTab
    CREDIT_WALLET_AVAILABLE = True
except ImportError:
    try:
        from credit_wallet_tab import CreditWalletTab
        CREDIT_WALLET_AVAILABLE = True
    except ImportError:
        CREDIT_WALLET_AVAILABLE = False
        print("[WARNING] CreditWalletTab not available")

# Define subscription checker availability
SUBSCRIPTION_CHECKER_AVAILABLE = has_supabase_client

# Import Supabase client untuk subscription checking
try:
    from modules_client.supabase_client import SupabaseClient
    SUPABASE_CLIENT_AVAILABLE = True
    # Define idle callbacks for Supabase
    def set_idle_callbacks(*args, **kwargs):
        pass
    def start_usage_tracking(*args, **kwargs):
        pass
    def stop_usage_tracking(*args, **kwargs):
        pass
except ImportError:
    SUPABASE_CLIENT_AVAILABLE = False
    # Fallback functions
    def set_idle_callbacks(*args, **kwargs):
        pass
    def start_usage_tracking(*args, **kwargs):
        pass
    def stop_usage_tracking(*args, **kwargs):
        pass

# Import update manager
try:
    from modules_client.update_manager import get_update_manager
    from ui.update_dialog import UpdateDialog
    UPDATE_MANAGER_AVAILABLE = True
except ImportError as e:
    print(f"[WARNING] Update manager not available: {e}")
    UPDATE_MANAGER_AVAILABLE = False

# Exception handler global
def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    print("Uncaught Exception:", exc_type.__name__, exc_value)
    
    # Log error to file
    error_log = Path("logs/error_log.txt")
    error_log.parent.mkdir(exist_ok=True)
    with open(error_log, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().isoformat()}] {exc_type.__name__}: {exc_value}\n")

sys.excepthook = handle_exception

# High-DPI policy
QGuiApplication.setHighDpiScaleFactorRoundingPolicy(
    Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
)

# Utility functions for simplifying hasattr checks
def safe_attr_check_legacy(obj, attr_name):
    """Check if object has attribute and it's truthy"""
    return safe_attr_check(obj, attr_name) and getattr(obj, attr_name)

def safe_timer_check(obj, timer_name):
    """Check if object has timer attribute and it's active"""
    return safe_attr_check(obj, timer_name) and getattr(obj, timer_name) and getattr(obj, timer_name).isActive()

class MainWindow(QMainWindow):
    # PERFORMANCE FIX: Fast startup mode
    FAST_STARTUP_MODE = True
    """Main window aplikasi StreamMate AI - Basic Mode Only."""
    
    def __init__(self):
        super().__init__()
        
        # Apply dark theme
        self.setStyleSheet(DARK_THEME)
        
        # Setup Supabase client for license validation
        self.supabase_client = SupabaseClient()
        
        # Log mode yang digunakan
        logger.info("StreamMate AI - Basic Mode Only")
        
        # Inisialisasi atribut penting
        self.validation_timer = None
        self.chat_listener_module = None
        self._credit_warning_shown = False
        self._no_credit_shown = False
        self._idle_warning_shown = False
        
        # Setup window properties
        self.setWindowTitle("StreamMate AI - Basic Mode")
        self.resize(1000, 700)
        self.setMinimumSize(800, 600)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Main widgets
        self.stack = QStackedWidget()
        self.stack.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setCentralWidget(self.stack)
        
        # Setup status bar
        self._setup_status_bar()
        
        # Setup icon jika tersedia
        self._setup_icon()
        
        # Load configuration
        self.cfg = ConfigManager("config/settings.json")
        version = "v1.0.0-basic"
        self.cfg.set("app_version", version)
        
        # Timer untuk demo expiration check - OPTIMASI: Kurangi frekuensi untuk performa
        self.demo_timer = QTimer(self)
        self.demo_timer.timeout.connect(self.check_demo_expiration)
        self.demo_timer.start(5000)  # ✅ OPTIMASI: Ubah dari 1 detik ke 5 detik untuk performa

        # Placeholder untuk tabs
        self.subscription_tab = None
        self.main_tabs = None
        self._subscription_tab_created = False
        
        # Session status timer - OPTIMASI: Perlambat interval
        self.session_timer = QTimer(self)
        self.session_timer.setInterval(120000)  # ✅ OPTIMASI: Ubah dari 60 detik ke 2 menit
        self.session_timer.timeout.connect(self.update_session_status)
        self.session_timer.start()
        
        # Setup idle callbacks jika tersedia
        if SUBSCRIPTION_CHECKER_AVAILABLE:
            set_idle_callbacks(
                warning_callback=self.show_idle_warning,
                timeout_callback=self.handle_idle_timeout
            )
        
        # Start license check timer - OPTIMASI: Perlambat interval  
        self.license_timer = QTimer(self)
        self.license_timer.timeout.connect(self.update_license_status)
        self.license_timer.start(600000)  # ✅ OPTIMASI: Ubah dari 5 menit ke 10 menit
        
        # Initial setup
        self.update_license_status()
        self._preload_chat_listener()
        
        # Handle startup flow
        self._handle_startup_flow()

        # Initialize update manager jika available
        if UPDATE_MANAGER_AVAILABLE:
            try:
                self.update_manager = get_update_manager()
                self.update_manager.update_available.connect(self.show_update_notification)
                logger.info("Update manager initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize update manager: {e}")
                self.update_manager = None
        else:
            self.update_manager = None

    def _setup_status_bar(self):
        """Setup status bar dengan label yang diperlukan."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # License status label
        self.license_label = QLabel()
        self.status_bar.addPermanentWidget(self.license_label)
        
        # Version label
        version_label = QLabel("StreamMate Basic v1.0.0")
        self.status_bar.addWidget(version_label)

    def _setup_icon(self):
        """Setup aplikasi icon jika tersedia."""
        icon_path = os.path.join(ROOT, "resources", "icons", "app_icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

    def _handle_startup_flow(self):
        """Handle alur startup berdasarkan kondisi login dan subscription dengan validasi lebih ketat"""
        from pathlib import Path
        import json
        import logging
        from datetime import datetime, timezone

        logger = logging.getLogger(__name__)

        token_file = Path("config/google_token.json")
        user_data = self.cfg.get("user_data", {})
        email = user_data.get("email", "")
        
        logger.info(f"Checking startup flow - Token exists: {token_file.exists()}, Email: {bool(email)}")
        
        # PERBAIKAN 1: Validasi token Google lebih ketat
        if token_file.exists() and email:
            try:
                # Validasi isi token file
                with open(token_file, "r", encoding="utf-8") as f:
                    token_data = json.load(f)
                    
                # Cek apakah token memiliki data yang valid
                if not token_data.get("token") or not token_data.get("refresh_token"):
                    logger.warning("Token file exists but incomplete, going to login")
                    self._show_login_tab()
                    return
                    
            except Exception as e:
                logger.error(f"Error reading token file: {e}")
                self._show_login_tab()
                return
            
            # PERBAIKAN 2: Validasi subscription lebih komprehensif
            subscription_file = Path("config/subscription_status.json")
            if subscription_file.exists():
                try:
                    with open(subscription_file, "r", encoding="utf-8") as f:
                        sub_data = json.load(f)
                        
                    status = sub_data.get("status", "")
                    hours_credit = float(sub_data.get("credit_balance", 0))
                    
                    logger.info(f"Subscription status: {status}, Hours: {hours_credit}")
                    
                    # CASE 1: Check for Pro package first - DENGAN VALIDASI KREDIT
                    pro_data = sub_data.get("pro", {})
                    basic_data = sub_data.get("basic", {})
                    
                    # ✅ PERBAIKAN UTAMA: Cek kredit sebelum mengaktifkan mode
                    if pro_data.get("active", False) and hours_credit > 0:
                        logger.info(f"Pro package is active with {hours_credit} credits, going to Pro mode")
                        self.pilih_paket("pro")
                        return
                    elif basic_data.get("active", False) and hours_credit > 0:
                        logger.info(f"Basic package is active with {hours_credit} credits, going to Basic mode")
                        self.pilih_paket("basic")
                        return
                    elif (pro_data.get("active", False) or basic_data.get("active", False)) and hours_credit <= 0:
                        logger.info(f"Package is active but no credits ({hours_credit}), staying in subscription tab")
                        self.login_berhasil()
                        return
                    # CASE 2: User berbayar dengan kredit cukup (fallback)
                    elif status in ["paid", "active"] and hours_credit >= 1.0:  # Minimal 1 kredit
                        logger.info(f"User has sufficient credit ({hours_credit}), going to basic mode")
                        self.pilih_paket("basic")
                        return
                        
                    # CASE 2: Demo masih aktif
                    elif status == "demo":
                        expire_date_str = sub_data.get("expire_date", "")
                        
                        # PERBAIKAN: Handle expire_date yang null dengan menghitung dari activated_at
                        if not expire_date_str or expire_date_str == "null":
                            activated_at_str = sub_data.get("activated_at", "")
                            demo_duration = sub_data.get("demo_duration_minutes", 30)
                            
                            if activated_at_str:
                                try:
                                    from datetime import datetime, timezone, timedelta
                                    activated_at = datetime.fromisoformat(activated_at_str)
                                    if activated_at.tzinfo is None:
                                        activated_at = activated_at.replace(tzinfo=timezone.utc)
                                    
                                    expire_date = activated_at + timedelta(minutes=demo_duration)
                                    expire_date_str = expire_date.isoformat()
                                    
                                    # Update file dengan expire_date yang benar
                                    sub_data["expire_date"] = expire_date_str
                                    with open(subscription_file, "w", encoding="utf-8") as f:
                                        json.dump(sub_data, f, indent=2, ensure_ascii=False)
                                    
                                    logger.info(f"Updated demo expire_date: {expire_date_str}")
                                except Exception as e:
                                    logger.error(f"Error calculating demo expire_date: {e}")
                                    return
                        
                        # ✅ PERBAIKAN UTAMA: Perhitungan waktu yang benar dengan timezone
                        if expire_date_str:
                            try:
                                from datetime import datetime, timezone
                                
                                # Parse expire date dengan timezone handling
                                if 'Z' in expire_date_str:
                                    expire_date_str = expire_date_str.replace('Z', '+00:00')
                                
                                    expire_date = datetime.fromisoformat(expire_date_str)
                                if expire_date.tzinfo is None:
                                    expire_date = expire_date.replace(tzinfo=timezone.utc)
                                
                                # Get current time in UTC for proper comparison
                                now_utc = datetime.now(timezone.utc)
                                    
                                logger.info(f"Demo check - Expire: {expire_date}, Now: {now_utc}")
                                
                                if now_utc < expire_date:
                                    remaining_time = expire_date - now_utc
                                    remaining_minutes = int(remaining_time.total_seconds() / 60)
                                    
                                    # Batasi maksimal 30 menit untuk demo
                                    if remaining_minutes > 30:
                                        remaining_minutes = 30
                                        logger.warning(f"Demo time capped at 30 minutes (was {remaining_minutes})")
                                    
                                    logger.info(f"Auto-resuming demo with {remaining_minutes} minutes remaining")
                                    self.log_info(f"Demo masih aktif: {remaining_minutes} menit tersisa")
                                    
                                    # Auto-navigate ke cohost tab
                                    QTimer.singleShot(100, lambda: self._navigate_to_cohost("basic"))
                                    return
                                else:
                                    logger.info("Demo has expired, staying in subscription tab")
                                    self.log_info("Demo telah berakhir")
                                    return
                                    
                            except Exception as e:
                                logger.error(f"Error parsing demo expire_date: {e}")
                                self.log_error(f"Error validasi demo: {e}")
                                return
                        
                    # CASE 3: Status tidak valid atau kredit habis
                    logger.info("Invalid subscription or insufficient credit, showing subscription tab")
                    self.login_berhasil()
                    return
                    
                except Exception as e:
                    logger.error(f"Error reading subscription file: {e}")
            
            # Tidak ada subscription file yang valid
            logger.info("No valid subscription file, showing subscription tab")
            self.login_berhasil()
        else:
            # Belum login atau email kosong
            logger.info("Not logged in or no email, showing login tab")
            self._show_login_tab()

    def _show_login_tab(self):
        """Tampilkan login tab."""
        self.login_tab = LoginTab(self)
        self.stack.addWidget(self.login_tab)

    def login_berhasil(self):
        """Show subscription tab after successful login dengan error handling yang lebih baik"""
        logger.info("login_berhasil() called")
        
        try:
            # PERBAIKAN: Reload config untuk memastikan data terbaru
            self.cfg.load_settings()
            
            # ✅ PERBAIKAN UTAMA: Tambah delay untuk memastikan file config ter-write sempurna
            import time
            time.sleep(0.1)  # 100ms delay untuk memastikan file operations selesai
            
            # Get user email dengan multiple fallback
            user_data = self.cfg.get("user_data", {})
            email = user_data.get("email", "")
            
            # Fallback: cek langsung dari config
            if not email:
                email = self.cfg.get("email", "")
            
            # Fallback: cek dari environment
            if not email:
                import os
                email = os.getenv("USER_EMAIL", "")
            
            if not email:
                logger.error("No email found in user data")
                # PERBAIKAN: Tampilkan dialog untuk input email manual jika diperlukan
                email, ok = QInputDialog.getText(
                    self, 
                    'Email Required', 
                    'Please enter your email address:'
                )
                if not ok or not email or "@" not in email:
                    self._show_login_tab()
                    return
                else:
                    # Simpan email yang diinput
                    self.cfg.set("user_data", {"email": email, "last_login": datetime.now().isoformat()})
                    logger.info(f"Email manually entered: {email}")
                
            logger.info(f"Using email for validation: {email}")
            
            # ✅ PERBAIKAN: Use Supabase client untuk validation
            # Set email di config untuk Supabase validation
            self.cfg.set("user_data", {"email": email, "last_login": datetime.now().isoformat()})
            logger.info(f"Email set for Supabase validation: {email}")
                
            # Validate license menggunakan Supabase - PENTING: Force refresh untuk selalu ambil data dari server
            license_data = self.supabase_client.validate_license(email)
            logger.info(f"License validation result: {license_data}")
            
            # PERBAIKAN: Pastikan subscription tab dibuat dengan benar
            if not safe_attr_check(self, 'subscription_tab') or self.subscription_tab is None:
                logger.info("Creating new subscription tab")
                from ui.subscription_tab import SubscriptionTab
                self.subscription_tab = SubscriptionTab(self)
                
            # Tambahkan ke stack jika belum ada
            if self.subscription_tab not in [self.stack.widget(i) for i in range(self.stack.count())]:
                logger.info("Adding subscription tab to stack")
                self.stack.addWidget(self.subscription_tab)
            
            # TAMBAHAN BARU: Refresh subscription tab untuk sinkronisasi data
            logger.info("Refreshing subscription tab to sync data")
            if safe_attr_check(self.subscription_tab, 'refresh_credits'):
                self.subscription_tab.refresh_credits()
                
            # Switch ke subscription tab
            self.stack.setCurrentWidget(self.subscription_tab)
            logger.info("Switched to subscription tab successfully")
            
            # Update status bar
            self.update_license_status()
            
            # PERBAIKAN: Cek apakah user sudah memiliki langganan valid
            # Support both direct is_valid and Supabase response format
            is_valid = (license_data.get("is_valid", False) or 
                       (license_data.get("status") == "success" and 
                        license_data.get("data", {}).get("is_valid", False)))
            
            if is_valid:
                # Extract data from either direct format or Supabase response
                if license_data.get("status") == "success" and "data" in license_data:
                    # Supabase response format
                    data = license_data["data"]
                    tier = data.get("tier", "basic")
                    credit_balance = float(data.get("credit_balance", data.get("hours_credit", 0)))
                    source = "supabase"
                else:
                    # Direct format
                    tier = license_data.get("tier", "basic")
                    credit_balance = float(license_data.get("credit_balance", license_data.get("hours_credit", 0)))
                    source = license_data.get("source", "unknown")
                
                # Tambahkan debug print untuk memahami alur program
                print(f"[DEBUG_STARTUP] Valid license found. Tier: {tier}, Credits: {credit_balance}, Source: {source}")
                
                # PERBAIKAN: Auto-resume demo mode jika masih aktif
                if source == "demo_active":
                    print(f"[DEBUG_STARTUP] Demo mode is active. Auto-resuming demo session.")
                    demo_remaining = license_data.get("demo_remaining", 0)
                    
                    # Auto-navigate ke cohost tab dengan mode basic
                    QTimer.singleShot(100, lambda: self._navigate_to_cohost("basic"))
                    return
                
                # PERBAIKAN: Cek dari file lokal jika server response tidak lengkap
                if credit_balance == 0:
                    try:
                        from pathlib import Path
                        import json
                        subscription_file = Path("config/subscription_status.json")
                        if subscription_file.exists():
                            with open(subscription_file, "r", encoding="utf-8") as f:
                                local_data = json.load(f)
                            credit_balance = float(local_data.get("credit_balance", local_data.get("hours_credit", 0)))
                            print(f"[DEBUG_STARTUP] Credit from local file: {credit_balance}")
                    except Exception as e:
                        print(f"[DEBUG_STARTUP] Error reading local credit: {e}")
                
                # PERBAIKAN: Jika user memiliki kredit yang cukup, langsung aktifkan mode basic
                if credit_balance >= 1.0:  # Minimal 1 kredit untuk basic mode
                    print(f"[DEBUG_STARTUP] User has sufficient credits ({credit_balance}). Activating {tier} mode.")
                    # Auto-activate jika sudah ada subscription
                    QTimer.singleShot(1500, lambda: self.pilih_paket(tier))
                    return
                
                # PERBAIKAN BARU: Jika user memiliki lisensi valid tapi kredit 0, tetap di subscription tab
                if credit_balance == 0:
                    print(f"[DEBUG_STARTUP] User has valid license but 0 credits. Staying in subscription tab.")
                    # Tetap di subscription tab, jangan auto-activate mode apapun
                    return
                    
                # Jika kredit habis, tampilkan notifikasi khusus
                print(f"[DEBUG_STARTUP] User has valid license but no credits. Showing credit exhausted notification.")
                QTimer.singleShot(2000, lambda: QMessageBox.information(
                    self,
                    "Credits Exhausted",
                    "Your credits have been exhausted.\n\nPlease buy additional credits to continue."
                ))
                return
                
            # Jika lisensi tidak valid atau tidak ada subscription
            print(f"[DEBUG_STARTUP] License validation result: Valid={license_data.get('is_valid', False)}, Message: {license_data.get('message')}")
            QTimer.singleShot(2000, lambda: QMessageBox.information(
                self,
                "Subscription Status",
                "Please check your subscription status.\n\nUse demo mode or buy credits to continue."
            ))
            
        except Exception as e:
            logger.error(f"Error in login_berhasil: {e}")
            import traceback
            traceback.print_exc()
            
            # Fallback ke login tab jika error
            self._show_login_tab()

    def check_demo_status(self):
        """Cek apakah demo masih aktif dengan validasi yang lebih baik."""
        from pathlib import Path
        import json
        from datetime import datetime, timezone

        subscription_file = Path("config/subscription_status.json")
        if not subscription_file.exists():
            return False

        try:
            data = json.loads(subscription_file.read_text(encoding="utf-8"))

            # Hanya proses jika status adalah demo
            if data.get("status") != "demo":
                return False

            expire_date_str = data.get("expire_date", "")
            if not expire_date_str:
                return False

            try:
                # Handle timezone dengan benar
                if '+' in expire_date_str:
                    expire_date = datetime.fromisoformat(expire_date_str)
                    now_time = datetime.now(timezone.utc)
                else:
                    expire_date = datetime.fromisoformat(expire_date_str)
                    now_time = datetime.now()

                # Cek apakah demo masih valid
                if now_time < expire_date:
                    remaining = expire_date - now_time
                    mins_left = int(remaining.total_seconds() / 60)
                    print(f"[INFO] Demo startup check: masih aktif, sisa {mins_left} menit")
                    return True
                else:
                    print(f"[INFO] Demo startup check: sudah expired")
                    # Update status ke expired
                    data["status"] = "expired"
                    subscription_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
                    return False

            except ValueError as e:
                print(f"[DEBUG] Error parsing expire_date: {e}")
                return False

        except Exception as e:
            print(f"[ERROR] Error in check_demo_status: {e}")
            return False

    def _check_purchased_packages(self):
        """Check which packages user has actually purchased"""
        try:
            subscription_file = Path("config/subscription_status.json")
            if not subscription_file.exists():
                return {"basic": False, "cohost_seller": False}
            
            with open(subscription_file, 'r', encoding='utf-8') as f:
                sub_data = json.load(f)
            
            # PERBAIKAN: Support both old and new subscription structures
            basic_active = False
            cohost_seller_active = False
            pro_active = False
            
            # Method 1: Check new structure (specific package purchases)
            if "basic" in sub_data and isinstance(sub_data["basic"], dict):
                basic_active = sub_data["basic"].get("active", False)
            
            if "cohost_seller" in sub_data and isinstance(sub_data["cohost_seller"], dict):
                cohost_seller_active = sub_data["cohost_seller"].get("active", False)
            
            if "pro" in sub_data and isinstance(sub_data["pro"], dict):
                pro_active = sub_data["pro"].get("active", False)
            
            # Method 2: Check old structure (general status + package + credits)
            if not basic_active and not cohost_seller_active and not pro_active:
                status = sub_data.get("status", "")
                package = sub_data.get("package", "")
                tier = sub_data.get("tier", "")
                credit_balance = float(sub_data.get("credit_balance", sub_data.get("hours_credit", 0)))
                is_valid = sub_data.get("is_valid", False)
                
                # PERBAIKAN KRITIS: User harus memiliki kredit > 0 untuk dianggap memiliki paket aktif
                if credit_balance <= 0:
                    print(f"[DEBUG] PACKAGE_CHECK: User has 0 credits, no active packages")
                    basic_active = False
                    cohost_seller_active = False
                    pro_active = False
                else:
                    # User has active subscription with credits = basic access
                    if (status in ["active", "paid"] and 
                        (package == "basic" or tier == "basic") and 
                        is_valid):
                        basic_active = True
                        print(f"[DEBUG] PACKAGE_CHECK: Detected basic access via old structure - Status: {status}, Credits: {credit_balance}")
                    
                    # Check for cohost_seller package
                    if (package == "cohost_seller" or tier == "cohost_seller") and is_valid:
                        cohost_seller_active = True
                        print(f"[DEBUG] PACKAGE_CHECK: Detected cohost_seller access via old structure")
                    
                    # Check for pro package
                    if (package == "pro" or tier == "pro") and is_valid:
                        pro_active = True
                        print(f"[DEBUG] PACKAGE_CHECK: Detected pro access via old structure")
            
            result = {
                "basic": basic_active,
                "cohost_seller": cohost_seller_active,
                "pro": pro_active
            }
            
            print(f"[DEBUG] PACKAGE_CHECK: Final result: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error checking purchased packages: {e}")
            return {"basic": False, "cohost_seller": False, "pro": False}

    def pilih_paket(self, paket):
        """Initialize main UI based on actually purchased packages."""
        print(f"[DEBUG] PILIH_PAKET: Called with paket: {paket}")
        
        try:
            logger.info(f"Memanggil pilih_paket dengan paket: {paket}")

            # ⚡ PERFORMANCE: Show loading indicator for mode switching
            self.statusBar().showMessage(f"Switching to {paket.upper()} mode...")
            
            # ⚡ PERFORMANCE: Skip package check if already cached and same mode
            if hasattr(self, '_last_mode') and self._last_mode == paket and hasattr(self, '_cached_purchased'):
                purchased = self._cached_purchased
                print(f"[DEBUG] PILIH_PAKET: Using cached packages: {purchased}")
            else:
                # Check what packages are actually purchased
                purchased = self._check_purchased_packages()
                self._cached_purchased = purchased
                self._last_mode = paket
                print(f"[DEBUG] PILIH_PAKET: Fresh packages check: {purchased}")

            # Determine which mode to use based on purchases
            # ✅ PERBAIKAN: Jika user memilih paket tertentu, gunakan paket tersebut
            if paket == "basic" and purchased["basic"]:
                actual_mode = "basic"
                # Force basic mode untuk memastikan tidak ada tab Pro
                purchased["force_basic"] = True
            elif paket == "pro" and purchased["pro"]:
                actual_mode = "pro"
                # Pastikan tidak force basic untuk Pro mode
                purchased["force_basic"] = False
            elif paket == "cohost_seller" and purchased["cohost_seller"]:
                actual_mode = "cohost_seller"
            # Fallback: jika paket yang dipilih tidak tersedia, gunakan yang tersedia
            elif purchased["pro"]:
                actual_mode = "pro"
                purchased["force_basic"] = False
            elif purchased["cohost_seller"]:
                actual_mode = "cohost_seller"
            elif purchased["basic"]:
                actual_mode = "basic"
                purchased["force_basic"] = True
            else:
                # No packages purchased - redirect to subscription tab
                print(f"[DEBUG] PILIH_PAKET: No packages purchased, redirecting to subscription")
                self._navigate_to_subscription_safely()
                return

            self.cfg.set("paket", actual_mode)
            print(f"[DEBUG] PILIH_PAKET: Using actual mode: {actual_mode}")

            # Create tabs based on purchased packages
            print(f"[DEBUG] PILIH_PAKET: Creating tabs for {actual_mode} mode")
            tabs = QTabWidget()
            tabs.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

            # Setup tabs based on purchased packages
            self._setup_tabs_by_packages(tabs, purchased)

            # Setup dan tampilkan main tabs
            self.main_tabs = tabs
            self.stack.addWidget(self.main_tabs)
            self.stack.setCurrentWidget(self.main_tabs)
            print(f"[DEBUG] PILIH_PAKET: Main tabs added to stack and set as current")

            # Update status
            if purchased["pro"]:
                self.status_bar.showMessage(f"StreamMate Pro activated", 5000)
            elif purchased["cohost_seller"]:
                self.status_bar.showMessage(f"StreamMate CoHost Seller activated", 5000)
            else:
                self.status_bar.showMessage(f"StreamMate Basic activated", 5000)
            print(f"[DEBUG] PILIH_PAKET: Status bar updated")

            # Start session tracking jika tersedia
            if SUBSCRIPTION_CHECKER_AVAILABLE:
                start_usage_tracking(f"init_{actual_mode}")

            print(f"[DEBUG] PILIH_PAKET: {actual_mode} mode berhasil diaktifkan")
            logger.info(f"{actual_mode} mode berhasil diaktifkan")
            
            # ⚡ PERFORMANCE: Update status bar to show successful mode switch
            self.statusBar().showMessage(f"{actual_mode.upper()} mode activated successfully", 3000)
            
            # Connect subscription tab signal
            if safe_attr_check(self, 'subscription_tab'):
                self.subscription_tab.package_activated.connect(self.activate_basic_mode_from_subscription)
                self.subscription_tab.demo_expired_signal.connect(self.handle_demo_expired)
            
        except Exception as e:
            print(f"[DEBUG] PILIH_PAKET: Error in pilih_paket: {e}")
            import traceback
            traceback.print_exc()
            
            # Fallback ke subscription tab
            try:
                self.subscription_tab = SubscriptionTab(self)
                self.stack.addWidget(self.subscription_tab)
                self.stack.setCurrentWidget(self.subscription_tab)
                print(f"[DEBUG] PILIH_PAKET: Fallback to subscription tab")
            except Exception as fallback_error:
                print(f"[DEBUG] PILIH_PAKET: Fallback also failed: {fallback_error}")

    def _setup_tabs_by_packages(self, tabs, purchased):
        """Setup tabs based on what packages user has purchased - OPTIMIZED with lazy loading"""
        try:
            print(f"[DEBUG] Setting up tabs for purchased packages: {purchased}")
            print(f"[DEBUG] Force basic mode: {purchased.get('force_basic', False)}")
            
            # ✅ OPTIMASI: Cache tab instances untuk menghindari re-initialization
            if not safe_attr_check(self, '_tab_cache'):
                self._tab_cache = {}
            
            # ✅ PERBAIKAN: Pisahkan logic untuk Basic dan Pro mode sesuai permintaan user
            if purchased["pro"] and not purchased.get("force_basic", False):
                # PRO MODE - sesuai permintaan user: cohost tab pro, credit wallet, chat overlay, profile, reply log, trakteer, tutorial, viewers, virtual mic, translate pro
                print("[INFO] Setting up PRO MODE tabs - sesuai permintaan user")
                print("[DEBUG] PRO MODE: Pro mode activated")
                
                # Tab Credit Wallet (PENTING untuk mode pro) - LAZY LOADING
                if CREDIT_WALLET_AVAILABLE:
                    if 'credit_wallet_tab' not in self._tab_cache:
                        self._tab_cache['credit_wallet_tab'] = CreditWalletTab()
                    self.credit_wallet_tab = self._tab_cache['credit_wallet_tab']
                    tabs.addTab(self.credit_wallet_tab, "💰 Credit Wallet")
                    print("[INFO] Credit Wallet tab added (Pro mode)")
                else:
                    if 'credit_wallet_placeholder' not in self._tab_cache:
                        placeholder = QWidget()
                        layout = QVBoxLayout(placeholder)
                        label = QLabel("💰 Credit Wallet\n\nModule not available.\nPlease check installation.")
                        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                        label.setStyleSheet("font-size: 16px; color: #888;")
                        layout.addWidget(label)
                        self._tab_cache['credit_wallet_placeholder'] = placeholder
                    tabs.addTab(self._tab_cache['credit_wallet_placeholder'], "💰 Credit Wallet")
                    print("[WARNING] Credit Wallet tab not available - using placeholder")
                
                # Tab CoHost Pro - LAZY LOADING
                if COHOST_PRO_AVAILABLE:
                    try:
                        print("[DEBUG] Attempting to initialize CohostTabPro...")
                        if 'cohost_pro_tab' not in self._tab_cache:
                            print("[DEBUG] Creating new CohostTabPro instance...")
                            self._tab_cache['cohost_pro_tab'] = CohostTabPro()
                            print("[DEBUG] CohostTabPro instance created successfully")
                        self.cohost_pro_tab = self._tab_cache['cohost_pro_tab']
                        tabs.addTab(self.cohost_pro_tab, "🤖 CoHost Pro")
                        print("[SUCCESS] CoHost Pro tab added (Pro mode)")
                    except Exception as e:
                        import traceback
                        error_details = traceback.format_exc()
                        logger.error(f"Failed to initialize CohostTabPro: {e}")
                        print(f"[ERROR] CohostTabPro initialization failed: {e}")
                        print(f"[ERROR] Full traceback:\n{error_details}")
                        if 'cohost_pro_placeholder' not in self._tab_cache:
                            placeholder = QWidget()
                            layout = QVBoxLayout(placeholder)
                            label = QLabel("🤖 CoHost Pro\n\nInitialization failed.\nPlease check logs for details.")
                            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                            label.setStyleSheet("font-size: 16px; color: #888;")
                            layout.addWidget(label)
                            self._tab_cache['cohost_pro_placeholder'] = placeholder
                        tabs.addTab(self._tab_cache['cohost_pro_placeholder'], "🤖 CoHost Pro")
                        print("[WARNING] CoHost Pro tab not available - using placeholder (init error)")
                else:
                    if 'cohost_pro_placeholder' not in self._tab_cache:
                        placeholder = QWidget()
                        layout = QVBoxLayout(placeholder)
                        label = QLabel("🤖 CoHost Pro\n\nModule not available.\nPlease check installation.")
                        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                        label.setStyleSheet("font-size: 16px; color: #888;")
                        layout.addWidget(label)
                        self._tab_cache['cohost_pro_placeholder'] = placeholder
                    tabs.addTab(self._tab_cache['cohost_pro_placeholder'], "🤖 CoHost Pro")
                    print("[WARNING] CoHost Pro tab not available - using placeholder")
                
                # Tab Chat Overlay - LAZY LOADING
                if OVERLAY_AVAILABLE:
                    if 'overlay_tab' not in self._tab_cache:
                        self._tab_cache['overlay_tab'] = OverlayTab()
                    self.overlay_tab = self._tab_cache['overlay_tab']
                    tabs.addTab(self.overlay_tab, "💬 Chat Overlay")
                    print("[INFO] Chat Overlay tab added (Pro mode)")
                
                # Tab Profile - LAZY LOADING
                if 'profile_tab' not in self._tab_cache:
                    self._tab_cache['profile_tab'] = ProfileTab(self)
                self.profile_tab = self._tab_cache['profile_tab']
                tabs.addTab(self.profile_tab, "👤 Profile")
                print("[INFO] Profile tab added (Pro mode)")
                
                # Tab Reply Log - LAZY LOADING
                if REPLY_LOG_AVAILABLE:
                    if 'reply_log_tab' not in self._tab_cache:
                        self._tab_cache['reply_log_tab'] = ReplyLogTab()
                    self.reply_log_tab = self._tab_cache['reply_log_tab']
                    tabs.addTab(self.reply_log_tab, "📝 Reply Log")
                    print("[INFO] Reply Log tab added (Pro mode)")
                
                # Tab Trakteer - LAZY LOADING
                if TRAKTEER_AVAILABLE:
                    if 'trakteer_tab' not in self._tab_cache:
                        self._tab_cache['trakteer_tab'] = TrakteerTab()
                    self.trakteer_tab = self._tab_cache['trakteer_tab']
                    tabs.addTab(self.trakteer_tab, "🎁 Trakteer")
                    print("[INFO] Trakteer tab added (Pro mode)")
                
                # Tab Tutorial - LAZY LOADING
                if TUTORIAL_AVAILABLE:
                    if 'tutorial_tab' not in self._tab_cache:
                        self._tab_cache['tutorial_tab'] = TutorialTab()
                    self.tutorial_tab = self._tab_cache['tutorial_tab']
                    tabs.addTab(self.tutorial_tab, "❓ Tutorial")
                    print("[INFO] Tutorial tab added (Pro mode)")
                
                # Tab Viewers - LAZY LOADING
                if VIEWERS_AVAILABLE:
                    if 'viewers_tab' not in self._tab_cache:
                        self._tab_cache['viewers_tab'] = ViewersTab()
                    self.viewers_tab = self._tab_cache['viewers_tab']
                    tabs.addTab(self.viewers_tab, "👥 Viewers")
                    print("[INFO] Viewers tab added (Pro mode)")
                
                # Tab Virtual Mic - LAZY LOADING
                if VIRTUAL_MIC_AVAILABLE:
                    if 'virtual_mic_tab' not in self._tab_cache:
                        self._tab_cache['virtual_mic_tab'] = VirtualMicTab()
                    self.virtual_mic_tab = self._tab_cache['virtual_mic_tab']
                    tabs.addTab(self.virtual_mic_tab, "🎚️ Virtual Mic")
                    print("[INFO] Virtual Mic tab added (Pro mode)")
                
                # Tab Translate Pro - LAZY LOADING
                if TRANSLATE_PRO_AVAILABLE:
                    if 'translate_tab_pro' not in self._tab_cache:
                        self._tab_cache['translate_tab_pro'] = TranslateTabPro()
                    self.translate_tab_pro = self._tab_cache['translate_tab_pro']
                    tabs.addTab(self.translate_tab_pro, "🌍 Translate Pro")
                    print("[INFO] Translate Pro tab added (Pro mode)")
                
                # ✅ HILANGKAN tab yang tidak diminta untuk Pro mode
                print("[INFO] Pro mode tabs: Credit Wallet, CoHost Pro, Chat Overlay, Profile, Reply Log, Trakteer, Tutorial, Viewers, Virtual Mic, Translate Pro")
                print("[INFO] Log, RAG, System Log tabs REMOVED from Pro mode as requested")
                
            elif purchased["basic"] or purchased.get("force_basic", False):
                # BASIC MODE - sesuai permintaan user: cohost tab basic, credit wallet, chat overlay, profile, reply log, trakteer, tutorial
                print("[INFO] Setting up BASIC MODE tabs - sesuai permintaan user")
                print("[DEBUG] BASIC MODE: Force basic mode activated")
                # Force basic mode untuk memastikan tidak ada tab Pro
                purchased["force_basic"] = True
                
                # Tab Credit Wallet (PENTING untuk mode basic) - LAZY LOADING
                if CREDIT_WALLET_AVAILABLE:
                    if 'credit_wallet_tab' not in self._tab_cache:
                        self._tab_cache['credit_wallet_tab'] = CreditWalletTab()
                    self.credit_wallet_tab = self._tab_cache['credit_wallet_tab']
                    tabs.addTab(self.credit_wallet_tab, "💰 Credit Wallet")
                    print("[INFO] Credit Wallet tab added (Basic mode)")
                else:
                    if 'credit_wallet_placeholder' not in self._tab_cache:
                        placeholder = QWidget()
                        layout = QVBoxLayout(placeholder)
                        label = QLabel("💰 Credit Wallet\n\nModule not available.\nPlease check installation.")
                        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                        label.setStyleSheet("font-size: 16px; color: #888;")
                        layout.addWidget(label)
                        self._tab_cache['credit_wallet_placeholder'] = placeholder
                    tabs.addTab(self._tab_cache['credit_wallet_placeholder'], "💰 Credit Wallet")
                    print("[WARNING] Credit Wallet tab not available - using placeholder")
                
                # Tab Cohost Basic - LAZY LOADING
                if COHOST_AVAILABLE:
                    if 'cohost_tab_basic' not in self._tab_cache:
                        self._tab_cache['cohost_tab_basic'] = CohostTabBasic()
                    self.cohost_tab = self._tab_cache['cohost_tab_basic']
                    tabs.addTab(self.cohost_tab, "🤖 Cohost Basic")
                    print("[INFO] Cohost Basic tab added (Basic mode)")
                else:
                    if 'cohost_basic_placeholder' not in self._tab_cache:
                        placeholder = QWidget()
                        layout = QVBoxLayout(placeholder)
                        label = QLabel("🤖 Cohost Basic\n\nModule not available.\nPlease check installation.")
                        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                        label.setStyleSheet("font-size: 16px; color: #888;")
                        layout.addWidget(label)
                        self._tab_cache['cohost_basic_placeholder'] = placeholder
                    tabs.addTab(self._tab_cache['cohost_basic_placeholder'], "🤖 Cohost Basic")
                    print("[WARNING] Cohost Basic tab not available - using placeholder")

                # Tab Chat Overlay - LAZY LOADING
                if OVERLAY_AVAILABLE:
                    if 'overlay_tab' not in self._tab_cache:
                        self._tab_cache['overlay_tab'] = OverlayTab()
                    self.overlay_tab = self._tab_cache['overlay_tab']
                    tabs.addTab(self.overlay_tab, "💬 Chat Overlay")
                    print("[INFO] Chat Overlay tab added (Basic mode)")

                # Tab Profile - LAZY LOADING
                if 'profile_tab' not in self._tab_cache:
                    self._tab_cache['profile_tab'] = ProfileTab(self)
                self.profile_tab = self._tab_cache['profile_tab']
                tabs.addTab(self.profile_tab, "👤 Profile")
                print("[INFO] Profile tab added (Basic mode)")

                # Tab Reply Log - LAZY LOADING
                if REPLY_LOG_AVAILABLE:
                    if 'reply_log_tab' not in self._tab_cache:
                        self._tab_cache['reply_log_tab'] = ReplyLogTab()
                    self.reply_log_tab = self._tab_cache['reply_log_tab']
                    tabs.addTab(self.reply_log_tab, "📝 Reply Log")
                    print("[INFO] Reply Log tab added (Basic mode)")
                
                # Tab Trakteer - LAZY LOADING
                if TRAKTEER_AVAILABLE:
                    if 'trakteer_tab' not in self._tab_cache:
                        self._tab_cache['trakteer_tab'] = TrakteerTab()
                    self.trakteer_tab = self._tab_cache['trakteer_tab']
                    tabs.addTab(self.trakteer_tab, "🎁 Trakteer")
                    print("[INFO] Trakteer tab added (Basic mode)")
                
                # Tab Tutorial - LAZY LOADING
                if TUTORIAL_AVAILABLE:
                    if 'tutorial_tab' not in self._tab_cache:
                        self._tab_cache['tutorial_tab'] = TutorialTab()
                    self.tutorial_tab = self._tab_cache['tutorial_tab']
                    tabs.addTab(self.tutorial_tab, "❓ Tutorial")
                    print("[INFO] Tutorial tab added (Basic mode)")
                
                # ✅ HILANGKAN tab yang tidak diminta untuk Basic mode
                print("[INFO] Basic mode tabs: Credit Wallet, Cohost Basic, Chat Overlay, Profile, Reply Log, Trakteer, Tutorial")
                print("[INFO] Viewers, Virtual Mic, Translate Pro tabs REMOVED from Basic mode as requested")
                
                # Connect signals for basic mode
                if safe_attr_check(self, 'cohost_tab') and safe_attr_check(self.cohost_tab, 'replyGenerated'):
                    # Connect ke reply log jika tersedia
                    if safe_attr_check(self, 'reply_log_tab'):
                        self.cohost_tab.replyGenerated.connect(self._handle_new_reply)
                        print("[INFO] Connected cohost to reply log")

                    # Connect ke overlay jika tersedia
                    if safe_attr_check(self, 'overlay_tab'):
                        self.cohost_tab.replyGenerated.connect(
                            lambda author, msg, reply: self.overlay_tab.update_overlay(author, reply)
                        )
                        print("[INFO] Connected cohost to overlay")
            else:
                # No packages purchased - show locked placeholders
                placeholder = QWidget()
                layout = QVBoxLayout(placeholder)
                label = QLabel("🔒 Features Locked\n\nPurchase Basic or Pro package with credits\nto unlock features")
                label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                label.setStyleSheet("font-size: 16px; color: #888;")
                layout.addWidget(label)
                tabs.addTab(placeholder, "🔒 Features Locked")
                print("[INFO] Features locked - user needs to purchase")

        except Exception as e:
            print(f"[ERROR] Error setting up tabs by packages: {e}")
            import traceback
            traceback.print_exc()

    def _handle_new_reply(self, author, message, reply):
        """Handler untuk meneruskan balasan baru ke reply_log_tab."""
        if safe_attr_check(self, 'reply_log_tab') and self.reply_log_tab:
            print(f"[DEBUG] Handling new reply from {author}: {message[:30]}...")

            if safe_attr_check(self.reply_log_tab, 'add_interaction'):
                self.reply_log_tab.add_interaction(author, message, reply)

            if safe_attr_check(self, 'overlay_tab') and self.overlay_tab:
                self.overlay_tab.update_overlay(author, reply)

    def update_license_status(self):
        """Update license status in status bar."""
        try:
            # Coba validasi license menggunakan Supabase - PENTING: Force refresh untuk selalu ambil data dari server
            try:
                email = self.get_user_email()
                if email:
                    license_data = self.supabase_client.validate_license(email)
                else:
                    # Fallback ke mode offline jika tidak ada email
                    license_data = {
                        "is_valid": True,
                        "tier": "basic",
                        "expire_date": "2025-12-31",
                        "offline_mode": True
                    }
            except Exception as e:
                logger.error(f"License validation error: {e}")
                # Fallback ke mode offline
                license_data = {
                    "is_valid": True,
                    "tier": "basic",
                    "expire_date": "2025-12-31",
                    "offline_mode": True
                }

            # 🔧 PERBAIKAN UTAMA: Check license status dari berbagai format response
            is_license_valid = False
            tier = "Basic"
            expire_date = None
            
            # Format 1: Direct is_valid field (fallback mode)
            if license_data.get("is_valid", False):
                is_license_valid = True
                tier = license_data.get("tier", "basic").title()
                expire_date = license_data.get("expire_date", "Unknown")
            
            # Format 2: VPS server response dengan data.is_active
            elif license_data.get("status") == "success" and license_data.get("data", {}).get("is_active", False):
                is_license_valid = True
                vps_data = license_data.get("data", {})
                tier = vps_data.get("tier", "basic").title()
                expire_date = vps_data.get("expire_date", "Unknown")
                logger.info("Using VPS server license validation")
            
            # Format 3: Check subscription file directly sebagai fallback
            elif not is_license_valid:
                try:
                    from pathlib import Path
                    import json
                    sub_file = Path("config/subscription_status.json")
                    if sub_file.exists():
                        with open(sub_file, 'r', encoding='utf-8') as f:
                            sub_data = json.load(f)
                        if sub_data.get("is_valid", False) and sub_data.get("status") == "active":
                            is_license_valid = True
                            tier = sub_data.get("tier", "basic").title()
                            expire_date = sub_data.get("expire_date")
                            logger.info("Using subscription file fallback for license display")
                except Exception as fallback_error:
                    logger.error(f"Fallback license check failed: {fallback_error}")

            if is_license_valid:
                # Update label status
                if expire_date and expire_date != "Unknown" and expire_date:
                    try:
                        expire_dt = datetime.fromisoformat(expire_date)
                        days_left = (expire_dt - datetime.now()).days

                        status_text = f"🔑 {tier} - {days_left} days"
                        if license_data.get("offline_mode"):
                            status_text += " (Offline)"
                        self.license_label.setText(status_text)

                        # Alert berdasarkan hari tersisa
                        if days_left <= 5:
                            self.license_label.setStyleSheet("color: red; font-weight: bold;")
                        else:
                            self.license_label.setStyleSheet("")

                    except Exception as e:
                        logger.error(f"Error parsing expire date: {e}")
                        self.license_label.setText(f"🔑 {tier} - Expires: {expire_date}")
                else:
                    # Untuk langganan tanpa expire date (credit-based)
                    status_text = f"🔑 {tier}"
                    if license_data.get("offline_mode"):
                        status_text += " (Offline)"
                    self.license_label.setText(status_text)
                    self.license_label.setStyleSheet("")  # Reset style untuk valid license
            else:
                self.license_label.setText("❌ No valid license")
                self.license_label.setStyleSheet("color: red;")

        except Exception as e:
            logger.error(f"Error updating license status: {e}")
            # Fallback ke mode offline
            self.license_label.setText("🔑 Basic (Offline)")

    def show_idle_warning(self, seconds_left):
        """Tampilkan peringatan idle."""
        mins_left = int(seconds_left / 60)
        if not safe_attr_check(self, '_idle_warning_shown') or not self._idle_warning_shown:
            self.status_bar.showMessage(f"⚠️ Idle detected. Session will pause in {mins_left} minutes.", 10000)
            self._idle_warning_shown = True

    def handle_idle_timeout(self):
        """Handle saat idle timeout tercapai."""
        self.status_bar.showMessage("Session paused due to inactivity. Interact to resume.", 10000)
        self._idle_warning_shown = False

    def update_session_status(self):
        """Update status sesi di status bar."""
        if safe_attr_check(self, 'license_label'):
            self.update_license_status()
            
    def check_demo_expiration(self):
        """Cek sisa waktu demo dan panggil handler jika waktu habis."""
        try:
            # Jangan proses jika main_tabs belum ada (misal masih di halaman login)
            if not safe_attr_check(self, 'main_tabs') or not self.main_tabs:
                return

            subscription_file = Path("config/subscription_status.json")
            if not subscription_file.exists():
                return

            with open(subscription_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            status = data.get("status", "")
            if status != "demo":
                # Hapus pesan demo dari status bar jika sudah tidak dalam mode demo
                if "Demo Mode" in self.status_bar.currentMessage():
                     self.status_bar.clearMessage()
                return

            expire_date_str = data.get("expire_date")
            if not expire_date_str:
                return

            wib = pytz.timezone('Asia/Jakarta')
            expire_date = datetime.fromisoformat(expire_date_str).astimezone(wib)
            now = datetime.now(wib)

            if now < expire_date:
                remaining = expire_date - now
                mins_left = int(remaining.total_seconds() / 60)
                secs_left = int(remaining.total_seconds() % 60)
                self.status_bar.showMessage(f"🎮 Demo Mode - Sisa waktu: {mins_left}m {secs_left}s", 2000)
            else:
                # --- PERBAIKAN INTI ADA DI SINI ---
                logger.warning("Waktu demo terdeteksi telah habis. Menjalankan handle_demo_expired.")
                
                # Hentikan timer ini agar tidak terpanggil berulang kali
                self.demo_timer.stop()
                
                # Hapus pesan dari status bar
                if "Demo Mode" in self.status_bar.currentMessage():
                     self.status_bar.clearMessage()
                
                # Panggil handler utama untuk proses demo expired
                self.handle_demo_expired()

        except Exception as e:
            logger.error(f"Error dalam check_demo_expiration: {e}")
            # Hentikan timer jika ada error berkelanjutan untuk mencegah spam log
            self.demo_timer.stop()


    def handle_demo_expired(self):
        """Handle demo mode expiration."""
        try:
            # ✅ PERBAIKAN UTAMA: Stop semua proses yang sedang berjalan
            print("[DEMO-EXPIRED] Demo 30 menit telah habis - menghentikan semua proses...")
            
            # 1. Stop timer demo terlebih dahulu
            if safe_attr_check(self, 'demo_timer'):
                self.demo_timer.stop()
                print("[DEMO-EXPIRED] Demo timer stopped")
                
            # 2. Stop auto-reply di cohost tab dengan lebih agresif
            if safe_attr_check(self, 'cohost_tab') and self.cohost_tab:
                try:
                    # Stop auto-reply jika sedang aktif
                    if safe_attr_check(self.cohost_tab, 'reply_busy') and self.cohost_tab.reply_busy:
                        self.cohost_tab.reply_busy = False
                        print("[DEMO-EXPIRED] Cohost auto-reply stopped")
                    
                    # Stop listener
                    if safe_attr_check(self.cohost_tab, 'stop') and callable(getattr(self.cohost_tab, 'stop')):
                        self.cohost_tab.stop()
                        print("[DEMO-EXPIRED] Cohost listener stopped")
                    
                    # Clear queue jika ada
                    if safe_attr_check(self.cohost_tab, 'reply_queue'):
                        self.cohost_tab.reply_queue.clear()
                        print("[DEMO-EXPIRED] Cohost reply queue cleared")
                        
                except Exception as e:
                    print(f"[DEMO-EXPIRED] Error stopping cohost: {e}")
            
            # 3. Update subscription status file
            from pathlib import Path
            import json
            from datetime import datetime
            subscription_file = Path("config/subscription_status.json")
            if subscription_file.exists():
                try:
                    with open(subscription_file, "r", encoding="utf-8") as f:
                        subscription_data = json.load(f)
                    
                    # Update status dari demo ke expired
                    subscription_data["status"] = "expired"
                    subscription_data["demo_expired_at"] = datetime.now().isoformat()
                    subscription_data["demo_used"] = True  # Tandai demo sudah digunakan
                    
                    with open(subscription_file, "w", encoding="utf-8") as f:
                        json.dump(subscription_data, f, indent=2, ensure_ascii=False)
                    
                    print("[DEMO-EXPIRED] Demo status updated to expired")
                    
                except Exception as e:
                    print(f"[DEMO-EXPIRED] Error updating demo status: {e}")
                
            # 4. Show user-friendly expiration message
            QMessageBox.information(
                self,
                "Demo Mode Finished",
                "30-minute demo has finished! 🕒\n\n"
                "✨ Demo will be available again tomorrow at 00:00 WIB\n"
                "💳 Or buy credit packages to continue using the app\n\n"
                "You will be redirected to the subscription page..."
            )
            
            # 5. Navigate to subscription tab dengan handling yang lebih baik
            self._navigate_to_subscription_safely()
            
            # 6. Refresh subscription tab UI dengan delay
            QTimer.singleShot(500, self._refresh_subscription_tab_UI)
            
            print("[DEMO-EXPIRED] Demo expiration handling completed")
            
        except Exception as e:
            print(f"[DEMO-EXPIRED] Error handling demo expiration: {e}")
            import traceback
            traceback.print_exc()

    def _refresh_subscription_tab_UI(self):
        """Refresh UI subscription tab setelah demo expired"""
        try:
            if safe_attr_check(self, 'subscription_tab'):
                # Call refresh_credits untuk update tombol demo
                if safe_attr_check(self.subscription_tab, 'refresh_credits'):
                    self.subscription_tab.refresh_credits()
                    print("[DEMO-EXPIRED] Subscription tab UI refreshed after demo expiration")
                
                # Update display juga jika ada
                if safe_attr_check(self.subscription_tab, 'update_display'):
                    self.subscription_tab.update_display()
                
        except Exception as e:
            print(f"[DEMO-EXPIRED] Error refreshing subscription tab UI: {e}")

    def _navigate_to_subscription_safely(self):
        """Navigate ke subscription tab dan stop semua listener aktif saat demo expired."""
        try:
            print("[DEMO-EXPIRED] Navigating to subscription tab...")
            
            # ✅ PERBAIKAN: Create atau show subscription tab
            if not safe_attr_check(self, 'subscription_tab'):
                from ui.subscription_tab import SubscriptionTab
                self.subscription_tab = SubscriptionTab(self)
                self.stack.addWidget(self.subscription_tab)
                print("[DEMO-EXPIRED] Created new subscription tab")
            
            # Set subscription tab sebagai current widget
            self.stack.setCurrentWidget(self.subscription_tab)
            print("[DEMO-EXPIRED] Switched to subscription tab")
            
            # Update status bar
            self.status_bar.showMessage("Demo expired - Redirected to subscription", 5000)
            
            # ✅ PERBAIKAN: Disable tab cohost jika ada main_tabs
            if safe_attr_check(self, 'main_tabs'):
                for i in range(self.main_tabs.count()):
                    tab_text = self.main_tabs.tabText(i)
                    
                    # Disable cohost tab
                    if "cohost" in tab_text.lower():
                        self.main_tabs.setTabEnabled(i, False)
                        print(f"[DEMO-EXPIRED] Disabled tab: {tab_text}")
        
        except Exception as e:
            print(f"[DEMO-EXPIRED] Error navigating to subscription: {e}")
            import traceback
            traceback.print_exc()

    def logout(self):
        """Handle logout request dari ProfileTab."""
        reply = QMessageBox.question(
            self, 'Logout Confirmation',
            'Are you sure you want to logout from the application?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            # Simpan email user untuk mempertahankan data saat login kembali
            email = self.cfg.get("user_data", {}).get("email", "")
            print(f"[LOGOUT] Starting logout process for {email}")
            
            # CRITICAL: Clear ALL caches untuk mengatasi bug EXE cache persistence
            try:
                if has_supabase_client:
                    # Use Supabase client for cache clearing
                    self.supabase_client = SupabaseClient()
                    # Clear local caches
                    print("[LOGOUT] Using Supabase client for cache clearing...")
                else:
                    # Fallback manual clearing
                    print("[LOGOUT] Using fallback cache clearing...")
                    
                    # Clear subscription status file
                    subscription_path = Path("config/subscription_status.json")
                    if subscription_path.exists():
                        subscription_path.unlink()
                        print(f"[LOGOUT] Cleared: {subscription_path}")
                    
                    # Clear temp files
                    temp_files = [
                        "temp/license_cache.json",
                        "temp/current_session.json",
                        "temp/daily_usage.json",
                        "temp/last_sync.json",
                        "temp/vps_cache.json"
                    ]
                    for temp_file in temp_files:
                        temp_path = Path(temp_file)
                        if temp_path.exists():
                            temp_path.unlink()
                            print(f"[LOGOUT] Cleared: {temp_file}")
                
            except Exception as e:
                print(f"[LOGOUT-ERROR] Cache clearing failed: {e}")
                # Continue with logout even if cache clearing fails
                import traceback
                traceback.print_exc()
            
            # Hapus token Google jika ada
            token_path = Path("config/google_token.json")
            if token_path.exists():
                try:
                    token_path.unlink()
                    print(f"[LOGOUT] Cleared Google token")
                except Exception as e:
                    print(f"[LOGOUT-ERROR] Error removing token: {e}")
            
            # Reset data user
            self.cfg.set("user_data", {})
            print(f"[LOGOUT] Cleared user data from config")
            
            # Track logout ke server jika memungkinkan - SKIP IN SUPABASE-ONLY MODE
            if email and not _is_supabase_only_mode():
                try:
                    import requests
                    response = requests.post(
                        "http://69.62.79.238:8000/api/email/track",
                        json={"email": email, "action": "logout"},
                        timeout=5
                    )
                    
                    if response.status_code == 200:
                        print(f"[LOGOUT] Logout tracked to server for {email}")
                    else:
                        print(f"[LOGOUT] Failed to track logout: {response.status_code}")
                        
                except Exception as e:
                    print(f"[LOGOUT] Logout tracking error: {e}")
            elif email and _is_supabase_only_mode():
                print(f"✅ Supabase-only mode: Skipping VPS logout tracking for {email}")
                
                # Fallback ke temp file untuk backward compatibility
                temp_file = Path("temp/last_logout_email.txt")
                temp_file.parent.mkdir(exist_ok=True)
                temp_file.write_text(email, encoding="utf-8")
                print(f"[LOGOUT] Saved logout email to temp file")
            
            # Hentikan semua proses aktif
            if safe_attr_check(self, 'main_tabs'):
                for i in range(self.main_tabs.count()):
                    tab = self.main_tabs.widget(i)
                    if safe_attr_check(tab, 'stop'):
                        try:
                            tab.stop()
                            print(f"[LOGOUT] Stopped tab {i}")
                        except:
                            pass
            
            # Buat tab login baru
            if not safe_attr_check(self, 'login_tab'):
                self.login_tab = LoginTab(self)
                self.stack.addWidget(self.login_tab)
            
            # Tampilkan tab login
            self.stack.setCurrentWidget(self.login_tab)
            
            # Hapus tab yang sudah tidak perlu
            if safe_attr_check(self, 'main_tabs'):
                self.stack.removeWidget(self.main_tabs)
                self.main_tabs = None
                print(f"[LOGOUT] Removed main tabs")
                
            if safe_attr_check(self, 'subscription_tab'):
                self.stack.removeWidget(self.subscription_tab)
                self.subscription_tab = None
                print(f"[LOGOUT] Removed subscription tab")
            
            # Tampilkan konfirmasi
            self.status_bar.showMessage("Successfully logged out - All caches cleared", 3000)
            print(f"[LOGOUT] ✅ Logout process completed for {email}")
            print(f"[LOGOUT] Ready for fresh login session")
            
    def _preload_chat_listener(self):
        """Pre-load chat_listener module for later use."""
        try:
            import importlib.util
            chat_listener_path = os.path.join(ROOT, "listeners", "chat_listener.py")
            if os.path.exists(chat_listener_path):
                spec = importlib.util.spec_from_file_location("chat_listener", chat_listener_path)
                self.chat_listener_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(self.chat_listener_module)
                print("[DEBUG] Chat listener module preloaded successfully")
        except Exception as e:
            print(f"[WARN] Failed to preload chat_listener module: {e}")
    
    def closeEvent(self, event):
        """Handle window close event."""
        try:
            print("[FORCE-CLOSE-DEBUG] MainWindow closeEvent triggered")
            
            # Stop license timer
            if safe_timer_check(self, 'license_timer'):
                print("[FORCE-CLOSE-DEBUG] Stopping license timer")
                self.license_timer.stop()
            
            # Stop validation timer
            if safe_timer_check(self, 'validation_timer'):
                print("[FORCE-CLOSE-DEBUG] Stopping validation timer")
                self.validation_timer.stop()
            
            # Stop session tracking jika tersedia
            if SUBSCRIPTION_CHECKER_AVAILABLE:
                print("[FORCE-CLOSE-DEBUG] Stopping usage tracking")
                stop_usage_tracking()
            
            # Ask for confirmation
            print("[FORCE-CLOSE-DEBUG] Showing exit confirmation dialog")
            reply = QMessageBox.question(
                self, 'Confirm Exit',
                'Are you sure you want to exit the application?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                print("[FORCE-CLOSE-DEBUG] User confirmed exit, stopping tabs")
                
                # Stop any active tabs before closing
                if safe_attr_check(self, 'main_tabs'):
                    print("[FORCE-CLOSE-DEBUG] Stopping main tabs")
                    current_tab = self.main_tabs.currentWidget()
                    if safe_attr_check(current_tab, 'stop'):
                        try:
                            print(f"[FORCE-CLOSE-DEBUG] Stopping current tab: {type(current_tab).__name__}")
                            current_tab.stop()
                        except Exception as e:
                            print(f"[FORCE-CLOSE-DEBUG] Error stopping current tab: {e}")
                    
                    for i in range(self.main_tabs.count()):
                        tab = self.main_tabs.widget(i)
                        if safe_attr_check(tab, 'stop'):
                            try:
                                print(f"[FORCE-CLOSE-DEBUG] Stopping tab {i}: {type(tab).__name__}")
                                tab.stop()
                            except Exception as e:
                                print(f"[FORCE-CLOSE-DEBUG] Error stopping tab {i}: {e}")
                
                # Accept event
                print("[FORCE-CLOSE-DEBUG] Accepting close event")
                event.accept()
            else:
                print("[FORCE-CLOSE-DEBUG] User cancelled exit")
                event.ignore()
                
        except Exception as e:
            print(f"[FORCE-CLOSE-DEBUG] Error in MainWindow closeEvent: {e}")
            import traceback
            print(f"[FORCE-CLOSE-DEBUG] Traceback: {traceback.format_exc()}")
            # Force accept event even if cleanup fails
            event.accept()

    def activate_basic_mode_from_subscription(self, package):
        """Aktifkan mode dari subscription tab."""
        try:
            logger.info(f"Activating {package} mode from subscription tab")
            
            if package == "pro":
                # Handle Pro activation
                QMessageBox.information(
                    self, "CoHost Pro Activated! 🚀",
                    "CoHost Pro package has been activated!\n\n"
                    "✅ All Basic features\n"
                    "✅ Sequential & Delay Mode\n"
                    "✅ Premium Google Chirp3 TTS\n"
                    "✅ Virtual Microphone\n"
                    "✅ Viewer Management\n"
                    "✅ Advanced Analytics\n\n"
                    "You can now access CoHost Pro features in the main tabs!"
                )
                
                # Navigate to CoHost Pro tab if available
                if safe_attr_check(self, 'main_tabs'):
                    for i in range(self.main_tabs.count()):
                        tab_text = self.main_tabs.tabText(i)
                        if "cohost pro" in tab_text.lower():
                            self.main_tabs.setCurrentIndex(i)
                            break
                else:
                    # Create main tabs if not exists
                    self.pilih_paket("pro")
                
                return
            
            if package == "cohost_seller":
                # Handle CoHost Seller activation
                QMessageBox.information(
                    self, "CoHost Seller Activated! 🛍️",
                    "CoHost Seller package has been activated!\n\n"
                    "✅ Product Management (2 slots)\n"
                    "✅ Smart Trigger System\n"
                    "✅ Auto OBS Scene Switch\n"
                    "✅ Sales Analytics\n"
                    "✅ Live Selling AI\n\n"
                    "You can now access CoHost Seller features in the main tabs!"
                )
                
                # Navigate to CoHost Seller tab if available
                if safe_attr_check(self, 'main_tabs'):
                    for i in range(self.main_tabs.count()):
                        tab_text = self.main_tabs.tabText(i)
                        if "cohost seller" in tab_text.lower():
                            self.main_tabs.setCurrentIndex(i)
                            break
                else:
                    # Create main tabs if not exists
                    self.pilih_paket("basic")
                
                return
            
            # Handle basic mode activation
            # Validasi kredit sekali lagi via Supabase
            email = self.cfg.get("user_data", {}).get("email", "")
            if email:
                try:
                    supabase = SupabaseClient()
                    credit_data = supabase.get_credit_balance(email)
                    if credit_data and credit_data.get("status") == "success":
                        data = credit_data.get("data", {})
                        basic_credits = float(data.get("basic_credits", 0))
                        if basic_credits < 5.0:
                            QMessageBox.warning(
                                self, "Insufficient Credits",
                                "Insufficient credits to activate Basic Mode.\n"
                                "Minimum 5 credits required."
                            )
                            return
                except Exception as e:
                    print(f"Error checking credits via Supabase: {e}")
                    # Fallback: allow activation if Supabase check fails
            
            # Aktifkan basic mode
            self.pilih_paket("basic")
            
            # Start session tracking
            if SUBSCRIPTION_CHECKER_AVAILABLE:
                start_usage_tracking("basic_mode_activated")
                
        except Exception as e:
            logger.error(f"Error activating {package} mode: {e}")
            QMessageBox.critical(
                self, "Error",
                f"Failed to activate {package} Mode: {str(e)}"
            )

    def show_subscription_tab(self):
        """Method helper untuk menampilkan subscription tab"""
        try:
            if not safe_attr_check(self, 'subscription_tab'):
                from ui.subscription_tab import SubscriptionTab
                self.subscription_tab = SubscriptionTab(self)
                self.stack.addWidget(self.subscription_tab)
            
            self.stack.setCurrentWidget(self.subscription_tab)
            logger.info("Subscription tab shown successfully")
            
        except Exception as e:
            logger.error(f"Error showing subscription tab: {e}")

    def _check_minimum_credit(self, hours_credit):
        """Cek apakah kredit mencukupi untuk mode basic"""
        MIN_CREDIT_REQUIRED = 1.0  # Minimal 1 kredit
        return hours_credit >= MIN_CREDIT_REQUIRED

    def show_update_notification(self, update_info):
        """Tampilkan dialog update dengan semua fitur."""
        try:
            if not UPDATE_MANAGER_AVAILABLE or not self.update_manager:
                return
            
            # Buat dan tampilkan update dialog
            update_dialog = UpdateDialog(self.update_manager, self)
            update_dialog.set_update_info(update_info)
            
            # Show dialog
            logger.info(f"Showing update notification for version {update_info.get('version')}")
            update_dialog.exec()
            
        except Exception as e:
            logger.error(f"Error showing update notification: {e}")
            # Fallback ke simple message box
            QMessageBox.information(
                self, "Update Available",
                f"StreamMate AI update {update_info.get('version', 'new')} is available!\n\n"
                "Please check manually for download."
            )

    def _navigate_to_cohost(self, mode="basic"):
        """Navigasi langsung ke tab cohost untuk auto-resume demo."""
        try:
            print(f"[DEBUG] Auto-navigating to cohost tab with mode: {mode}")
            
            # Jika main_tabs belum ada, buat dulu dengan pilih_paket
            if not safe_attr_check(self, 'main_tabs') or not self.main_tabs:
                self.pilih_paket(mode)
                
            # Pastikan main_tabs sudah ada
            if safe_attr_check(self, 'main_tabs') and self.main_tabs:
                # Cari tab cohost
                for i in range(self.main_tabs.count()):
                    tab_text = self.main_tabs.tabText(i)
                    if "cohost" in tab_text.lower():
                        # Aktifkan tab cohost
                        self.main_tabs.setCurrentIndex(i)
                        print(f"[DEBUG] Successfully navigated to cohost tab at index {i}")
                        return True
                        
            print("[DEBUG] Could not find cohost tab")
            return False
            
        except Exception as e:
            print(f"[ERROR] Error navigating to cohost tab: {e}")
            import traceback
            traceback.print_exc()
            return False

    def update_credit_display(self):
        """Update credit display di UI"""
        try:
            subscription_file = Path("config/subscription_status.json")
            
            if subscription_file.exists():
                with open(subscription_file, 'r', encoding='utf-8') as f:
                    sub_data = json.load(f)
                    
                # PERBAIKAN: Gunakan field baru 'credit_balance' bukan 'hours_credit'
                hours_credit = float(sub_data.get("credit_balance", 0))
                
                # Update credit label
                self.credit_label.setText(f"{hours_credit:.2f} jam")
                
            else:
                self.credit_label.setText("0.00 jam")
                
        except Exception as e:
            print(f"Error updating credit display: {e}")
            self.credit_label.setText("0.00 jam")

    def get_user_email(self):
        """Get current user email from config"""
        try:
            user_data = self.cfg.get("user_data", {})
            return user_data.get("email", "")
        except:
            return ""

    def refresh_license_data(self):
        """Refresh license data dari Supabase"""
        try:
            # Get user email
            email = self.get_user_email()
            if not email:
                return
            
            # Call Supabase API
            supabase = SupabaseClient()
            credit_data = supabase.get_credit_balance(email)
            
            if credit_data and credit_data.get("status") == "success":
                data = credit_data.get("data", {})
                
                # Update UI dengan data Supabase - show total credits
                wallet_balance = float(data.get("wallet_balance", 0))
                basic_credits = float(data.get("basic_credits", 0))
                pro_credits = float(data.get("pro_credits", 0))
                total_credits = wallet_balance + basic_credits + pro_credits
                
                self.credit_label.setText(f"{total_credits:.2f} jam")
                
            else:
                print(f"Supabase API error: {credit_data}")
            
        except Exception as e:
            print(f"Error refreshing license data: {e}")