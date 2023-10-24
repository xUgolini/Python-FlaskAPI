from flask_restful import Resource, reqparse
from models.usuario import UserModel
from tokensRevogados import tokens_revogados
from flask_jwt_extended import create_access_token, jwt_required, get_jwt
import bcrypt

atributos = reqparse.RequestParser()
atributos.add_argument('login', type=str, required=True, help="Campo deve ser preenchido.")
atributos.add_argument('senha', type=str, required=True, help="Campo deve ser preenchido.")
    
class User(Resource):
    # /usuario/{user_id}
    def get(self, user_id):
        user = UserModel.find_user(user_id)

        if user:
            return user.json()
        return {'message': 'Usuário não encontrado.'}, 404

    @jwt_required()
    def delete(self, user_id):
        usuario_encontrado = UserModel.find_user(user_id)
        if usuario_encontrado:
            try:
                usuario_encontrado.delete_user()
            except:
                return {"message": 'Erro interno do servidor.'}, 500
            return {"message": 'Usuário deletado.'}
        return {'message': 'Usuário não encontrado.'}, 404

class UserRegister(Resource):
    # /cadastro
    def post(self):
        dados = atributos.parse_args()

        if UserModel.find_by_login(dados['login']):
            return {"message": "O login '{}' já existe.".format(dados['login'])}
        
        hashed_password = bcrypt.hashpw(dados['senha'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        dados['senha'] = hashed_password
        
        user = UserModel(**dados)
        user.save_user()
        return {'message': 'Usuário criado com sucesso'}, 201 #created
        
class UserLogin(Resource):

    @classmethod
    def post(cls):
        dados = atributos.parse_args()

        user = UserModel.find_by_login(dados['login'])

        if user and bcrypt.checkpw(dados['senha'].encode('utf-8'), user.senha.encode('utf-8')):
            token_de_acesso = create_access_token(identity=user.user_id)
            return {'acess_token': token_de_acesso}, 200
        return {"message": 'Usuario ou senha incorretos.'}, 401 #Unauthorized
    
class UserLogout(Resource):

    @jwt_required()
    def post(self):
        jwt_id = get_jwt()['jti'] # JWT Token Identifier
        tokens_revogados.add(jwt_id)
        return {'message': 'Logged out successfully'}, 200