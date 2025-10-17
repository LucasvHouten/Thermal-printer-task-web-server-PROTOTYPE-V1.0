import os
import time
import threading
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("printer.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import thermy library for printer communication
try:
    import thermy
    THERMY_AVAILABLE = True
except ImportError:
    logger.error("Thermy library not found. Please install it from https://github.com/mazoqui/thermy")
    THERMY_AVAILABLE = False

class PrinterManager:
    def __init__(self):
        self.printer = None
        self.is_connected = False
        self.connection_lock = threading.Lock()
        
    def connect(self):
        """Connect to the Bluetooth printer"""
        if not THERMY_AVAILABLE:
            logger.error("Thermy library not available. Cannot connect to printer.")
            return False
            
        with self.connection_lock:
            if self.is_connected:
                return True
                
            try:
                logger.info("Attempting to connect to the thermal printer...")
                self.printer = thermy.Printer()
                self.is_connected = True
                logger.info("Connected to thermal printer successfully")
                return True
            except Exception as e:
                logger.error(f"Failed to connect to printer: {str(e)}")
                self.is_connected = False
                return False
    
    def disconnect(self):
        """Disconnect from the printer"""
        with self.connection_lock:
            if self.is_connected and self.printer:
                try:
                    self.printer.close()
                    logger.info("Disconnected from thermal printer")
                except Exception as e:
                    logger.error(f"Error disconnecting from printer: {str(e)}")
                finally:
                    self.is_connected = False
                    self.printer = None
    
    def print_task(self, task):
        """Print a task to the thermal printer"""
        if not self.connect():
            logger.error("Cannot print task - printer not connected")
            return False
            
        try:
            # Print header
            self.printer.bold(True)
            self.printer.text_center(f"TASK: {task.title}")
            self.printer.bold(False)
            self.printer.feed(1)
            
            # Print description with word wrap
            self.printer.text(f"Description:\n{task.description}")
            self.printer.feed(1)
            
            # Print date and time
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
            self.printer.text(f"Printed: {current_time}")
            self.printer.text(f"Scheduled: {task.print_datetime.strftime('%Y-%m-%d %H:%M')}")
            
            # If it's a reminder, indicate that
            if task.is_reminder_printed and not task.is_printed:
                self.printer.bold(True)
                self.printer.text("\nREMINDER")
                self.printer.bold(False)
            
            # Final line feed
            self.printer.feed(4)
            self.printer.cut()
            
            logger.info(f"Successfully printed task: {task.id} - {task.title}")
            return True
            
        except Exception as e:
            logger.error(f"Error printing task: {str(e)}")
            return False

# Create a singleton printer manager instance
printer_manager = PrinterManager()
