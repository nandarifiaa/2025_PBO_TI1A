# models/task.py
from datetime import datetime

class Task:
    def __init__(self, title, description='', completed=False, deadline=None, attachment=''):
        self.title = title
        self.description = description
        self.completed = completed
        self.deadline = deadline  # YYYY-MM-DD string
        self.attachment = attachment

    def mark_complete(self):
        self.completed = True

    def is_near_deadline(self):
        if not self.deadline:
            return False
        try:
            deadline_date = datetime.strptime(self.deadline, '%Y-%m-%d').date()
            days_remaining = (deadline_date - datetime.today().date()).days
            return 0 <= days_remaining <= 3
        except:
            return False

    def __str__(self):
        status = "✓" if self.completed else "✗"
        return f"{status} {self.title} (DL: {self.deadline or '-'})"