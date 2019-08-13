
from flask_restful import Resource, reqparse
from flask_jwt_extended import (
	jwt_required,
	get_jwt_claims,
	jwt_optional,
	get_jwt_identity,
	fresh_jwt_required
	)
from models.item import ItemModel 


class Item(Resource):
	#cannot do this
	#@app.route('/student/<string:name>')
	
	parser = reqparse.RequestParser()
	parser.add_argument('price',
						type = float,
						required = True,
						help = "This filed cannot be left blank!"
	)
	
	parser.add_argument('store_id',
						type = int,
						required = True,
						help = "Every item needs a store id!"
	)
	
	@jwt_required  #need authenticate before calling the jwt method.
	def get(self, name):
		
		item = ItemModel.find_by_name(name)
		if item:
			return item.json()		
		return {'message' : 'Item not found'}, 404
	

	@fresh_jwt_required
	def post(self, name):
	
		if ItemModel.find_by_name(name):
			return {'message' : "An item with name '{}' already exists.".format(name)}, 400
		
		data = Item.parser.parse_args()
		item = ItemModel(name, **data) #data['price'], data['store_id'])
		
		try:
			item.save_to_db()
		except:
			return {"message": 'An error occurred inserting the item.'}
		
		return item.json(), 201   #201 created, 202 accepted, 200 OK. 


				
	@jwt_required  #need authenticate before calling the jwt method. 	
	def delete(self, name):
		claims = get_jwt_claims()
		if not claims['is_admin']:
			return {'message' : 'Admin priviledge required.'}, 401
		item = ItemModel.find_by_name(name)
		if item:
			item.delete_from_db()
			return {'message': 'Item deleted.'}
		return {'message': 'Item not found.'}, 404

	def put(self, name):

		data = Item.parser.parse_args()	
		item = ItemModel.find_by_name(name)
		
		if item is None:
			item = ItemModel(name, **data) #data['price'], data['store_id'])
		else:
			item.price = data['price']
			
		item.save_to_db()
		
		return item.json()
		
		

class ItemList(Resource):

	@jwt_optional
	def get(self):
		user_id = get_jwt_identity()
		items = list(map(lambda x : x.json(), ItemModel.find_all()))
		if user_id:
			return {'items' : items, 'user_id' : user_id}, 200
		return {'items': [item['name'] for item in items],
				'message' : 'More data available if you log in.',
				'user_id' : user_id }, 200

