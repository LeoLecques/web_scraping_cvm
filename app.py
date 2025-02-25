from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'senha_teste' 

def get_db_connection():
    conn = sqlite3.connect('web_scraping_cvm.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_table_names():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    table_names = [row['name'] for row in cursor.fetchall()]
    conn.close()
    return table_names

def format_table_name(name):
    name = name.replace('fre_cia_aberta_', '').replace('_', ' ')
    return ' '.join(word.capitalize() for word in name.split())

@app.route('/')
def index():
    table_names = get_table_names()
    formatted_names = {name: format_table_name(name) for name in table_names}
    return render_template('index.html', table_names=formatted_names)

@app.route('/table/<table_name>')
@app.route('/table/<table_name>/<int:page>')
def view_table(table_name, page=1):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name=?;", (table_name,))
    if cursor.fetchone()[0] != 1:
        return "Erro: Tabela não encontrada", 404

    offset = (page - 1) * 20
    query = f"SELECT * FROM `{table_name}` LIMIT 20 OFFSET ?;"
    
    cursor.execute(query, (offset,))
    data = cursor.fetchall()
    column_names = [column[0] for column in cursor.description]
    
    cursor.execute("SELECT COUNT(*) FROM `{}`;".format(table_name))
    total_count = cursor.fetchone()[0]
    total_pages = (total_count - 1) // 20 + 1
    
    formatted_names = {name: format_table_name(name) for name in get_table_names()}
    
    conn.close()
    return render_template('view_table.html', data=data, column_names=column_names, page=page, total_pages=total_pages, table_names=formatted_names, table_name=table_name)

@app.route('/update/<table_name>/<int:id>', methods=['POST'])
def update_row(table_name, id):
    conn = get_db_connection()
    cursor = conn.cursor()
    data = request.form
    set_clause = ', '.join([f"{key} = ?" for key in data.keys()])
    values = list(data.values()) + [id]
    cursor.execute(f"UPDATE `{table_name}` SET {set_clause} WHERE id = ?", values)
    conn.commit()
    conn.close()
    flash('Registro atualizado com sucesso!', 'success')
    return redirect(url_for('view_table', table_name=table_name))

@app.route('/delete/<table_name>/<int:id>', methods=['POST'])
def delete_row(table_name, id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM `{table_name}` WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash('Registro deletado com sucesso!', 'success')
    return redirect(url_for('view_table', table_name=table_name))

if __name__ == '__main__':
    app.run(debug=True)

