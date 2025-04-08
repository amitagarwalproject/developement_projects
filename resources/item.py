import uuid
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from db import db
from sqlalchemy.exc import SQLAlchemyError
from models import ItemModel
from schemas import ItemSchema, ItemUpdateSchema

blp = Blueprint("Items", __name__, description= "Operations on items")


@blp.route("/item")
class ItemList(MethodView):
    @blp.response(200,ItemSchema(many=True))
    def get(self):
        return ItemModel.query.all()

    # @blp.arguments(ItemSchema) - This decorator tells Flask to:Parse the request body using the ItemSchema,
    # Validate the input (based on required=True,
    # types, etc.),Deserialize the JSON payload into a Python dictionary
    # Instead of manually calling request.get_json(),
    # you get item_data as a clean Python dictionary with validated fields
    @blp.arguments(ItemSchema)
    @blp.response(200,ItemSchema)
    # @blp.response(200, ItemSchema)
    # Purpose: This sets the expected response schema and status code.
    #
    # It tells Flask to:
    #
    # Serialize the return value (usually a dictionary) using ItemSchema
    #
    # Return a 200 OK response
    #
    # Auto-generate Swagger documentation for it too!
    def post(self,item_data):  # item_data is passed by @blp.arguments — it’s your validated request data.
        item = ItemModel(**item_data)

        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message= "An error occurred while inserting the item")

        return item


@blp.route("/item/<string:item_id>")
class Item(MethodView):
    @blp.response(200,ItemSchema)
    def get(self,item_id):
        item = ItemModel.query.get_or_404(item_id)
        return item

    @blp.arguments(ItemUpdateSchema)
    @blp.response(200,ItemSchema)
    def put(self,item_data,item_id):
        item = ItemModel.query.get(item_id)
        if item:
            item.price = item_data["price"]
            item.name = item_data["name"]
        else:
            item = ItemModel(id = item_id, **item_data)

        db.session.add(item)
        db.session.commit()
        return item

    def delete(self,item_id):
        item = ItemModel.query.get_or_404(item_id)
        db.session.delete(item)
        db.session.commit()
        return {"message": "Item deleted"}




