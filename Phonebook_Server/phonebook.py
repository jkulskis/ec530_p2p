from flask import Flask, Response
from flask_restful import Api, Resource, reqparse, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy
import hashlib

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///peers.db'
db =  SQLAlchemy(app)

class PeerModel(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String,nullable=False)
    IP = db.Column(db.String,nullable=False)
    port = db.Column(db.Integer,nullable=False)
    key = db.Column(db.String,nullable=False)
    def __repr__(self):
        rep = f'{self.username} @ {self.IP}:{self.port}'
        return rep

db.create_all()

peer_fields = {
    'username': fields.String,
    'IP': fields.String,
    'port': fields.Integer
}

post_args = reqparse.RequestParser(bundle_errors=True)
post_args.add_argument('IP', type=str, required=True, help='Invalid IP address')
post_args.add_argument('port', type=int, required=True, help='Invalid port #')
post_args.add_argument('password', type=str, required=True, help='Invalid password')

put_args = reqparse.RequestParser(bundle_errors=True)
put_args.add_argument('IP', type=str, required=False, help='Invalid IP address')
put_args.add_argument('port', type=int, required=False, help='Invalid port #')
put_args.add_argument('password', type=str, required=True, help='Invalid password')

delete_args = reqparse.RequestParser(bundle_errors=True)
delete_args.add_argument('password', type=str, required=True, help='Invalid password')

class PeerResource(Resource):
    def post(self, username):
        args = post_args.parse_args()
        peer = PeerModel.query.filter_by(username=username).first()
        if peer is not None:
            return Response(status=409)
        peer = PeerModel(
            username = username,
            IP = args['IP'],
            port = args['port'],
            key = hashlib.md5(args['password'].encode()).hexdigest()
        )
        db.session.add(peer)
        db.session.flush()
        db.session.commit()
        return Response(status=201)

    @marshal_with(peer_fields)
    def get(self, username):
        peer = PeerModel.query.filter_by(username=username).first()
        return peer

    def delete(self,username):
        args = delete_args.parse_args()
        peer = PeerModel.query.filter_by(username=username).first()
        if peer is None:
            return Response(status=404)
        print(peer.key)
        if peer.key != hashlib.md5(args['password'].encode()).hexdigest():
            return Response(status=401)
        db.session.delete(peer)
        db.session.commit()
        return Response(status=200)

class PeersResource(Resource):
    @marshal_with(peer_fields)
    def get(self):
        peers = PeerModel.query.all()
        return peers


api.add_resource(PeerResource,'/peers/<string:username>')
api.add_resource(PeersResource,'/peers/')

if __name__ == '__main__':
    app.run(debug=False)