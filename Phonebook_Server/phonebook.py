"""
TODO: Add put method
"""
from flask import Flask, Response
from flask_restful import Api, Resource, reqparse, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy
import hashlib
from cryptography.fernet import Fernet
import json

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///peers.db'
db =  SQLAlchemy(app)

class PeerModel(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.LargeBinary,nullable=False)
    IP = db.Column(db.LargeBinary,nullable=False)
    port = db.Column(db.LargeBinary,nullable=False)
    key = db.Column(db.String,nullable=False)
    def __repr__(self):
        rep = '{ "username": "' + self.username.decode() + '", '
        rep = rep + '"IP": "' + self.IP.decode() + '", '
        rep = rep + '"port": "' + self.port.decode() + '" }'
        return rep

db.create_all()

post_args = reqparse.RequestParser(bundle_errors=True)
post_args.add_argument('IP', type=str, required=True, help='Invalid IP address')
post_args.add_argument('port', type=int, required=True, help='Invalid port #')
post_args.add_argument('password', type=str, required=True, help='Invalid password')

# put_args = reqparse.RequestParser(bundle_errors=True)
# put_args.add_argument('IP', type=str, required=False, help='Invalid IP address')
# put_args.add_argument('port', type=int, required=False, help='Invalid port #')
# put_args.add_argument('password', type=str, required=True, help='Invalid password')

delete_args = reqparse.RequestParser(bundle_errors=True)
delete_args.add_argument('password', type=str, required=True, help='Invalid password')

class PeerResource(Resource):
    def __init__(self) -> None:
        super().__init__()
        self.key = b'nL1fSi8HQHG9kh3Lex7jqNbPnjVgSqzhnVrtsDb14pA='
        self.fernet = Fernet(self.key)
        
    def post(self, username):
        args = post_args.parse_args()
        peers = PeerModel.query.all()
        for peer in peers:
            if self.fernet.decrypt(peer.username) == username.encode():
                return Response(status=409)
        peer = PeerModel(
            username = self.fernet.encrypt(username.encode()),
            IP = self.fernet.encrypt(args['IP'].encode()),
            port = self.fernet.encrypt(str(args['port']).encode()),
            key = hashlib.md5(args['password'].encode()).hexdigest()
        )
        db.session.add(peer)
        db.session.flush()
        db.session.commit()
        return Response(status=201)

    def schema(self, peer: PeerModel) -> json:
        JSON = json.loads(str(peer))
        JSON['username'] = self.fernet.decrypt(JSON['username'].encode()).decode()
        JSON['IP'] = self.fernet.decrypt(JSON['IP'].encode()).decode()
        JSON['port'] = int(self.fernet.decrypt(JSON['port'].encode()).decode())
        return JSON

    def get(self, username):
        peers = PeerModel.query.all()
        for peer in peers:
            if self.fernet.decrypt(peer.username) == username.encode():
                return self.schema(peer)
        return Response(status=404)

    def delete(self,username):
        args = delete_args.parse_args()
        peers = PeerModel.query.all()
        for peer in peers:
            if self.fernet.decrypt(peer.username) == username.encode():
                if peer.key != hashlib.md5(args['password'].encode()).hexdigest():
                    return Response(status=401)
                db.session.delete(peer)
                db.session.commit()
                return Response(status=200)
        return Response(status=404)        

class PeersResource(Resource):
    def __init__(self) -> None:
        super().__init__()
        self.key = b'nL1fSi8HQHG9kh3Lex7jqNbPnjVgSqzhnVrtsDb14pA='
        self.fernet = Fernet(self.key)

    def schema(self, peer: PeerModel) -> json:
        JSON = json.loads(str(peer))
        JSON['username'] = self.fernet.decrypt(JSON['username'].encode()).decode()
        JSON['IP'] = self.fernet.decrypt(JSON['IP'].encode()).decode()
        JSON['port'] = int(self.fernet.decrypt(JSON['port'].encode()).decode())
        return JSON

    def get(self):
        peers = PeerModel.query.all()
        schemas = []
        for peer in peers:
            schemas.append(self.schema(peer))
        return schemas

    # def delete(self):
    #     peers = PeerModel.query.all()
    #     for peer in peers:
    #         db.session.delete(peer)
    #     db.session.commit()
    #     return Response(status = 200)

api.add_resource(PeerResource,'/peers/<string:username>')
api.add_resource(PeersResource,'/peers/')

if __name__ == '__main__':
    app.run(debug=True)