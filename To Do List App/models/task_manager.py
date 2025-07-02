# models/task_manager.py
from models.task import Task

class TaskManager:
    def __init__(self):
        self.tasks = []

    def add_task(self, task: Task):
        """Menambahkan agenda baru ke dalam daftar."""
        self.tasks.append(task)

    def remove_task(self, index: int):
        """Menghapus agenda berdasarkan indeks."""
        if 0 <= index < len(self.tasks):
            del self.tasks[index]

    def complete_task(self, index: int):
        """Menandai agenda sebagai selesai."""
        if 0 <= index < len(self.tasks):
            self.tasks[index].mark_complete()

    def to_dict(self):
        """Mengubah daftar agenda menjadi list of dict."""
        return [vars(task) for task in self.tasks]

    def load_from_dict(self, data):
        """Memuat agenda dari list of dict."""
        self.tasks = [Task(**t) for t in data]