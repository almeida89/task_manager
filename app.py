"""
Personal Task Manger - Main Application
=======================================

Um aplicativo web simples para gerenciar tarefas pessoais usando Flask.
Este projeto demonstra conceitos básicos de Python incluindo:
- Classes e objetos
- Manipulação de arquivos JSON
- Desenvolvimento web com Flask
- Tratamento de erros
- Estrutura de dados
"""

from flask import Flask, render_template, request, redirect, url_for, jsonify
from datetime import datetime
from flask import flash
import json
import os

# Importar nossas classes personalizadas
from models.task import Task
from utils.file_manager import FileManager

# Configuração da aplicação FLask
app = Flask(__name__)
app.secret_key = 'task_manager_secret_key_2025' # Chave para sessões e mensagens flash

# Instanciar o gerenciamento de arquivos
file_manager = FileManager()

@app.route('/')
def index():
    """
    Página inicial - exibe todas as tarefas
    
    Returns:
        Renderiza o template index.html com listas de tarefas
    """
    try:
        # Carregar todas as tarefas do arquivo JSON
        tasks = file_manager.load_tasks()
        
        # Contar estatísticas das tarefas
        total_tasks = len(tasks)
        completed_tasks = sum(1 for task in tasks if task['completed'])
        pending_tasks = total_tasks - completed_tasks
        
        # Preparar dados para o template
        stats = {
            'total': total_tasks,
            'completed': completed_tasks,
            'pendind': pending_tasks
        }
        
        return render_template('index.html', tasks=tasks, stats=stats)
    
    except Exception as e:
        # Em caso de erro, exibir mensagem e lista vazia
        flash(f'Erro ao carregar tarefas: {str(e)}', 'error')
    
    return render_template('index.html', tasks=[], stats={'total': 0, 'completed': 0, 'pending': 0})
    
@app.route('/add_task', methods=['POST'])
def add_task():
    """
    Adiciona uma nova tarefa ao sistema
    
    Returns:
        Redirect para página inicial
    """
    try:
        # Obter dados do formulário
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        priority = request.form.get('priority', 'medium')
        
        # Validar se o título não está vazio
        if not title:
            flash('Título da tarefa é obrigatório', 'error')
            return redirect(url_for('index'))
        
        # Criar nova instância de tarefa
        new_task = Task(title=title, description=description, priority=priority)
        
        # Salvar a tarefa
        success = file_manager.add_task(new_task.to_dict())
        
        if success:
            flash(f'Tarefa "{title} adicionada com sucesso!', 'success')
        else:
            flash('Erro ao adicionar tarefa', 'error')
    
    except Exception as e:
        flash(f'Erro inesperado: {str(e)}', 'error')
        
    return redirect(url_for('index'))

@app.route('/toggle_task/<int:task_id>')
def toggle_task(task_id):
    """
    Alterna o status de conclusão de uma tarefa
    
    Args:
        task_id(int): ID da tarefa a ser alterada
        
    Returns:
        Redirect para página inicial
    """
    try:
        success = file_manager.toggle_task(task_id)
        
        if success:
            flash('Status da tarefa alterado com sucesso!', 'success')
        else:
            flash('Tarefa não encontrada', 'error')
    
    except Exception as e:
        flash(f'Erro ao alterar tarefa: {str(e)}', 'error')
        
    return redirect(url_for('index'))

@app.route('/delete_task/<int:task_id>')
def delete_task(task_id):
    """
    Remove uma tarefa do sistema
    
    Args:
        task_id (int): ID da tarefa a ser removida
    
    Returns:
        Redirect para página inicial
    """
    try:
        success = file_manager.delete_task(task_id)
        
        if success:
            flash('Tarefa removida com sucesso!', 'success')
        else:
            flash('Tarefa não encontrada', 'error')
            
    except Exception as e:
        flash(f'Erro ao remover tarefa: {str(e)}', 'error')
        
    return redirect(url_for('index'))

@app.route('/api/tasks')
def api_tasks():
    """
    API endpoint para obter todas as tarefas em formato JSON
    
    Returns:
        JSON com lista de tarefas
    """
    try:
        tasks = file_manager.load_tasks()
        return jsonify({'tasks': tasks, 'count': len(tasks)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.errorhandler(404)
def not_found(error):
    """ Manipula erros 404 (página não encontrada)"""
    return render_template('error.html', error_code = 404, message = 'Página não encontrada'), 404

@app.errorhandler(500)
def internal_error(error):
    """ Manipula erros 500 (erro interno do servidor)"""
    return render_template('error.html', error_code = 500, message = 'Erro interno do servidor'), 500

if __name__ == '__main__':
    # Garantir que o diretório de dados existe
    os.makedirs('data', exist_ok=True)
    
    # Executar aplicação em modo de desenvolvimento
    print("Ininiando Gerenciador de tarefas...")
    print("Acesse: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)