from flask import Flask, request, jsonify, render_template, send_from_directory
from models.user import User
from database import db
from flask_login import LoginManager , login_user , current_user, logout_user, login_required

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager(app)
login_manager.init_app(app)
#view para login
login_manager.login_view = 'login'
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route('/login', methods=["POST"])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if username and password:
        #Logica de login
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            print(current_user.is_authenticated)
            return jsonify({"message": "Credenciais validas"})

    return jsonify({"message": "Credenciais invalidas"}), 400

@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Deslogado com sucesso"})


@app.route('/user', methods=['POST'])
@login_required
def create_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if username and password:
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "Usuario criado com sucesso"})
    
    return jsonify({"message": "Dados invalidos"}), 400
    

@app.route('/user/<int:user_id>', methods=['GET'])
@login_required
def read_user(user_id):
    user = User.query.get(user_id)
    if user:
        return jsonify({"username": user.username})
    return jsonify({"message": "Usuario nao encontrado"}), 404


@app.route('/user/<int:user_id>', methods=['PUT'])
@login_required
def update_user(user_id):
    data = request.get_json()
    user = User.query.get(user_id)
    if user:
        user.password = data.get('password')
        db.session.commit()
        return jsonify({"message": f"Usuario {user_id} atualizado com sucesso"})
    return jsonify({"message": "Usuario nao encontrado"}), 404


@app.route('/user/<int:user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
    user = User.query.get(user_id)
    if user.id == current_user.id:
        return jsonify({"message": "Nao autorizado"}), 403
    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": f"Usuario {user_id} deletado com sucesso"})
    return jsonify({"message": "Usuario nao encontrado"}), 404



if __name__ == '__main__':
    app.run(debug=True)