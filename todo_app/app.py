from flask import Flask, render_template, request, redirect
import json
import os
from datetime import datetime

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

@app.route('/add', methods=['POST'])
def add_task():
    new_task_text = request.form['task']
    if new_task_text:
        # задание 3: добавляем дату создания
        new_task = {
            'text': new_task_text,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M')
        }
        tasks.append(new_task)
        save_tasks(tasks)
    return redirect('/')

@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    if 0 <= task_id < len(tasks):
        tasks.pop(task_id)
        save_tasks(tasks)
    return redirect('/')

@app.route('/clear', methods=['POST'])
def clear_all():
    tasks.clear()
    save_tasks(tasks)
    return redirect('/')

@app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    if task_id < 0 or task_id >= len(tasks):
        return "Задача не найдена", 404
    
    task = tasks[task_id]
    
    if request.method == 'POST':
        new_text = request.form.get('task', '').strip()
        
        old_text = task['text']
        
        if new_text == '':
            return render_template('edit.html', task=task, message="Текст не может быть пустым!")
        
        if new_text == old_text:
            return render_template('edit.html', task=task, message="Ничего не изменено")
        
        tasks[task_id]['text'] = new_text
        save_tasks(tasks)
        return redirect('/')
    
    return render_template('edit.html', task=tasks[task_id])

if __name__ == '__main__':
    app.run(debug=True)
