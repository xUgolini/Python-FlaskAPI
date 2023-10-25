from flask_restful import Resource
from models.site import SiteModel

class Sites(Resource):
    def get(self):
        return {'sites': [site.json() for site in SiteModel.query.all()]}
    
class Site(Resource):
    def get(self, url):
        site = SiteModel.find_site(url)
        if site:
            return site.json()
        return {'message': 'Site não encontrado.'}, 404 # Not found

    def post(self, url):
        if SiteModel.find_site(url):
            return {'message': "O site '{}'' já existe."}, 400 # Bad request
        site = SiteModel(url)
        try:
            site.save_site()
        except:
            return {'message': 'Erro interno do servidor'}, 500
        return site.json()

    def delete(self, url):
        site = SiteModel.find_site(url)
        if not site:
            return {'message': 'Site não encontrado.'}, 404 # Not found
        try:
            site.delete_site()
        except:
            return {'message': 'Erro interno do servidor'}, 500
        return {'message': 'Site deletado com sucesso.'}, 200 # OK