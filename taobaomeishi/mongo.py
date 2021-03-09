from sshtunnel import SSHTunnelForwarder
import pymongo
from config import *

def connect_mongo():
	return connect_to_mongo(SSH_IP, SSH_PORT, SSH_USER, SSH_PASSWORD, MONGO_IP, MONGO_PORT, MONGO_DB, MONGO_TABLE)

def connect_to_mongo(SSH_IP,SSH_PORT,SSH_USER,SSH_PASSWORD,MONGO_IP,MONGO_PORT,MONGO_DB,MONGO_TABLE):
	server = SSHTunnelForwarder((SSH_IP,SSH_PORT),ssh_username = SSH_USER,
		ssh_password = SSH_PASSWORD,remote_bind_address = (MONGO_IP,MONGO_PORT),
		local_bind_address=('0.0.0.0', 27017))
	server.start()
	client = pymongo.MongoClient(host = MONGO_IP)
	db = client[MONGO_DB]
	return db
