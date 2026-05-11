from flask import Flask, render_template, request, redirect
import json
import os
from datetime import datetime, date

app = Flask(__name__)

FILE_NAME = 'tasks.json'

def load_tasks():
    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_tasks(tasks):
    with open(FILE_NAME, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)

tasks = load_tasks()

@app.route('/')
def index():
    return render_template('index.html', tasks=tasks)

@app.route('/active')
def show_active():
    """Показывает только активные (невыполненные) задачи"""
    active_tasks = [task for task in tasks if not task.get('done', False)]
    return render_template('index.html', tasks=active_tasks)

@app.route('/completed')
def show_completed():
    """Показывает только выполненные задачи"""
    completed_tasks = [task for task in tasks if task.get('done', False)]
    return render_template('index.html', tasks=completed_tasks)

# НОВЫЙ МАРШРУТ: Сортировка по приоритету
@app.route('/by_priority')
def by_priority():
    """Сортирует все задачи по приоритету (высокий → средний → низкий)"""
    priority_order = {'высокий': 3, 'средний': 2, 'низкий': 1}
    sorted_tasks = sorted(
        tasks,
        key=lambda task: priority_order.get(task.get('priority', 'средний'), 2),
        reverse=True
    )
    return render_template('index.html', tasks=sorted_tasks)

# НОВЫЙ МАРШРУТ: Активные задачи, отсортированные по приоритету
@app.route('/by_priority_active')
def by_priority_active():
    """Показывает только активные (невыполненные) задачи, отсортированные по приоритету"""
    priority_order = {'высокий': 3, 'средний': 2, 'низкий': 1}
    active_tasks = [task for task in tasks if not task.get('done', False)]
    sorted_tasks = sorted(
        active_tasks,
        key=lambda task: priority_order.get(task.get('priority', 'средний'), 2),
        reverse=True
    )
    return render_template('index.html', tasks=sorted_tasks)

@app.route('/add', methods=['POST'])
def add_task():
    new_task = request.form.get('task')
    priority = request.form.get('priority', 'средний')  # ДОБАВЛЕНО: получаем приоритет
    
    if new_task:
        today = date.today().strftime('%Y-%m-%d')
        # ДОБАВЛЕНО: поле priority
        tasks.append({
            'text': new_task,
            'date': today,
            'done': False,
            'priority': priority
        })
        save_tasks(tasks)
    return redirect('/')

@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    if 0 <= task_id < len(tasks):
        tasks.pop(task_id)
        save_tasks(tasks)
    return redirect('/')

@app.route('/toggle/<int:task_id>')
def toggle_task(task_id):
    """Переключает статус выполнения задачи"""
    if 0 <= task_id < len(tasks):
        tasks[task_id]['done'] = not tasks[task_id].get('done', False)
        save_tasks(tasks)
    return redirect('/')

@app.route('/clear', methods=['POST'])
def clear_all():
    tasks.clear()
    save_tasks(tasks)
    return redirect('/')

@app.route('/complete-all', methods=['POST'])
def complete_all():
    """Отмечает все задачи как выполненные"""
    for task in tasks:
        task['done'] = True
    save_tasks(tasks)
    return redirect('/')

@app.route('/uncomplete-all', methods=['POST'])
def uncomplete_all():
    """Снимает отметку выполнения со всех задач"""
    for task in tasks:
        task['done'] = False
    save_tasks(tasks)
    return redirect('/')

# ИЗМЕНЁННЫЙ МАРШРУТ: теперь редактирует и текст, и приоритет
@app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    if task_id < 0 or task_id >= len(tasks):
        return "Задача не найдена", 404
    
    task = tasks[task_id]
    
    if request.method == 'POST':
        new_text = request.form.get('task', '').strip()
        new_priority = request.form.get('priority', 'средний')  # ДОБАВЛЕНО
        old_text = task['text']
        old_priority = task.get('priority', 'средний')  # ДОБАВЛЕНО
        
        if new_text == '':
            return render_template('edit.html', task=task, message="Текст не может быть пустым!")
        
        # ИЗМЕНЕНО: проверяем оба поля
        if new_text == old_text and new_priority == old_priority:
            return render_template('edit.html', task=task, message="Ничего не изменено")
        
        task['text'] = new_text
        task['priority'] = new_priority  # ДОБАВЛЕНО
        save_tasks(tasks)
        return redirect('/')
    
    return render_template('edit.html', task=task)

if __name__ == '__main__':
    app.run(debug=True)