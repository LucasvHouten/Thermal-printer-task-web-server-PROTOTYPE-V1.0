import logging
from datetime import datetime, timedelta
from app import db
from app.models import Task
from app.printer import printer_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scheduler.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def initialize_scheduler(scheduler):
    """Set up the scheduler jobs"""
    # Check for tasks to print every minute
    scheduler.add_job(check_tasks_to_print, 'interval', minutes=1, id='check_tasks_job')
    
    # Try to connect to the printer every 5 minutes if not connected
    scheduler.add_job(ensure_printer_connected, 'interval', minutes=5, id='printer_connection_job')
    
    logger.info("Scheduler initialized with task printing jobs")

def ensure_printer_connected():
    """Ensure the printer is connected, try to reconnect if needed"""
    if not printer_manager.is_connected:
        printer_manager.connect()

def check_tasks_to_print():
    """Check for tasks that need to be printed"""
    now = datetime.utcnow()
    
    # Get tasks that should be printed now
    tasks_to_print = Task.query.filter(
        Task.print_datetime <= now,
        Task.is_printed == False
    ).all()
    
    for task in tasks_to_print:
        logger.info(f"Printing task {task.id}: {task.title}")
        if printer_manager.print_task(task):
            task.is_printed = True
            db.session.commit()
    
    # Check for reminders to print
    reminders_to_print = Task.query.filter(
        Task.reminder_minutes.isnot(None),
        Task.is_printed == True,
        Task.is_reminder_printed == False
    ).all()
    
    for task in reminders_to_print:
        reminder_time = task.print_datetime + timedelta(minutes=task.reminder_minutes)
        if now >= reminder_time:
            logger.info(f"Printing reminder for task {task.id}: {task.title}")
            if printer_manager.print_task(task):
                task.is_reminder_printed = True
                db.session.commit()

def schedule_task_print(task_id):
    """Manually trigger printing of a specific task"""
    task = Task.query.get(task_id)
    if task:
        logger.info(f"Manually printing task {task.id}: {task.title}")
        if printer_manager.print_task(task):
            task.is_printed = True
            db.session.commit()
            return True
    return False
