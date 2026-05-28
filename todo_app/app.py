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

# ========== ПР №7: ПОИСК ==========
@app.route('/search')
def search():
    """Поиск задач по тексту (без учёта регистра)"""
    query = request.args.get('q', '').strip().lower()
    if query:
        filtered_tasks = [task for task in tasks if query in task['text'].lower()]
    else:
        filtered_tasks = tasks
    return render_template('index.html', tasks=filtered_tasks, search_query=query)

# ========== ПР №8: СОРТИРОВКА ==========
@app.route('/sort/date')
def sort_by_date():
    """Сортировка по дате (новые сверху)"""
    sorted_tasks = sorted(tasks, key=lambda t: t.get('date', ''), reverse=True)
    return render_template('index.html', tasks=sorted_tasks)

@app.route('/sort/status')
def sort_by_status():
    """Сортировка по статусу (сначала активные, потом выполненные)"""
    sorted_tasks = sorted(tasks, key=lambda t: t.get('done', False))
    return render_template('index.html', tasks=sorted_tasks)

@app.route('/sort/priority')
def sort_by_priority():
    """Сортировка по приоритету (высокий → средний → низкий)"""
    priority_order = {'высокий': 1, 'средний': 2, 'низкий': 3}
    sorted_tasks = sorted(
        tasks,
        key=lambda t: priority_order.get(t.get('priority', 'средний'), 2)
    )
    return render_template('index.html', tasks=sorted_tasks)

@app.route('/sort/alpha')
def sort_by_alpha():
    """Сортировка по алфавиту (А → Я)"""
    sorted_tasks = sorted(tasks, key=lambda t: t.get('text', '').lower())
    return render_template('index.html', tasks=sorted_tasks)

# ========== ОСТАЛЬНЫЕ МАРШРУТЫ ==========
@app.route('/add', methods=['POST'])
def add_task():
    new_task = request.form.get('task')
    priority = request.form.get('priority', 'средний')
    
    if new_task:
        today = date.today().strftime('%Y-%m-%d')
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
    for task in tasks:
        task['done'] = True
    save_tasks(tasks)
    return redirect('/')

@app.route('/uncomplete-all', methods=['POST'])
def uncomplete_all():
    for task in tasks:
        task['done'] = False
    save_tasks(tasks)
    return redirect('/')

@app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    if task_id < 0 or task_id >= len(tasks):
        return "Задача не найдена", 404
    
    task = tasks[task_id]
    
    if request.method == 'POST':
        new_text = request.form.get('task', '').strip()
        new_priority = request.form.get('priority', 'средний')
        old_text = task['text']
        old_priority = task.get('priority', 'средний')
        
        if new_text == '':
            return render_template('edit.html', task=task, message="Текст не может быть пустым!")
        
        if new_text == old_text and new_priority == old_priority:
            return render_template('edit.html', task=task, message="Ничего не изменено")
        
        task['text'] = new_text
        task['priority'] = new_priority
        save_tasks(tasks)
        return redirect('/')
    
    return render_template('edit.html', task=task)

if __name__ == '__main__':
    app.run(debug=True)