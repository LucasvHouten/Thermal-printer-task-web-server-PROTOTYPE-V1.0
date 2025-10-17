from datetime import datetime
from app import db

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    print_datetime = db.Column(db.DateTime, nullable=False)
    reminder_minutes = db.Column(db.Integer, nullable=True)
    is_printed = db.Column(db.Boolean, default=False)
    is_reminder_printed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Task {self.title}>'
        
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'print_datetime': self.print_datetime.strftime('%Y-%m-%d %H:%M'),
            'reminder_minutes': self.reminder_minutes,
            'is_printed': self.is_printed,
            'is_reminder_printed': self.is_reminder_printed,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M')
        }
