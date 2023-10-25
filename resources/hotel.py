from flask_restful import Resource, reqparse
from models.hotel import HotelModel
from flask_jwt_extended import jwt_required
class Hoteis(Resource):
    def get(self):
        path_params = reqparse.RequestParser()
        path_params.add_argument('cidade', type=str)
        path_params.add_argument('estrelas_min', type=float)
        path_params.add_argument('estrelas_max', type=float)
        path_params.add_argument('diaria_min', type=float)
        path_params.add_argument('diaria_max', type=float)
        path_params.add_argument('limit', type=int)
        path_params.add_argument('offset', type=int)

        dados = path_params.parse_args()

        cidade = dados['cidade']
        estrelas_min = dados['estrelas_min'] or 0
        estrelas_max = dados['estrelas_max'] or 5
        diaria_min = dados['diaria_min'] or 0
        diaria_max = dados['diaria_max'] or 10000
        limit = dados['limit'] or 50
        offset = dados['offset'] or 0

        hoteis = HotelModel.find_by_params(cidade, estrelas_min, estrelas_max, diaria_min, diaria_max, limit, offset)
        return {'hoteis': [hotel.json() for hotel in hoteis]}
    
class Hotel(Resource):

    argumentos = reqparse.RequestParser()
    argumentos.add_argument('nome', type=str, required=True, help="O campo deve ser preenchido.")
    argumentos.add_argument('estrelas', type=float, required=True, help="O campo deve ser preenchido.")
    argumentos.add_argument('diaria')
    argumentos.add_argument('cidade')

    def get(self, hotel_id):
        hotel = HotelModel.find_hotel(hotel_id)

        if hotel:
            return hotel.json()
        return {'message': 'Hotel não encontrado.'}, 404
    
    @jwt_required()
    def post(self, hotel_id):
        if HotelModel.find_hotel(hotel_id):
            return {"message": "Hotel id '{}' já existe.".format(hotel_id)}, 400
        dados = Hotel.argumentos.parse_args()
        hotel = HotelModel(hotel_id, **dados)
        try:
            hotel.save_hotel()
        except:
            return {"message": 'Erro interno do servidor.'}, 500
        return hotel.json()

    @jwt_required()
    def put(self, hotel_id):
        dados = Hotel.argumentos.parse_args()
        hotel_encontrado = HotelModel.find_hotel(hotel_id)

        if hotel_encontrado:
            hotel_encontrado.update_hotel(**dados)
            hotel_encontrado.save_hotel()
            return hotel_encontrado.json(), 200
        hotel = HotelModel(hotel_id, **dados)
        try:
            hotel.save_hotel()
        except:
            return {"message": 'Erro interno do servidor.'}, 500
        return hotel.json(), 201

    @jwt_required()
    def delete(self, hotel_id):
        hotel_encontrado = HotelModel.find_hotel(hotel_id)
        if hotel_encontrado:
            try:
                hotel_encontrado.delete_hotel()
            except:
                return {"message": 'Erro interno do servidor.'}, 500
            return {"message": 'Hotel deletado.'}
        return {'message': 'Hotel não encontrado.'}, 404
