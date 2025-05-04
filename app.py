import os
from flask import Flask, jsonify
from flask_smorest import Api
from resources.item import blp as ItemBlueprint
from resources.store import blp as StoreBlueprint
from resources.tag import blp as TagBlueprint
from resources.user import blp as UserBlueprint
from db import db
from flask_jwt_extended import JWTManager


def create_app(db_url=None):
    app = Flask(__name__)

    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["API_TITLE"] = "Stores Rest API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv("DATABASE_URL","sqlite:///data.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)  # connecting sqlalchemy with flask app

    app.config["JWT_SECRET_KEY"] = "jose"

    api = Api(app) # initializing the Flask-Smorest Api object and binding it to your Flask app.
    '''It wraps your Flask app and adds support for:

    📋 Auto-generated Swagger/OpenAPI documentation.

    🛡️ Request validation via Marshmallow schemas.

    🎯 Route organization using blueprints.

    📦 Input parsing and output formatting made easy.'''

    jwt = JWTManager(app)

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header,jwt_payload):
        return(
            jsonify({"message": "The token has expired.", "error": "token_expired"}),
            401
        )

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return(
            jsonify(
                {"message": "Signature verification failed.", "error":"Invalid_token"}
            ),401
        )

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return(
            jsonify(
                {
                    "description": "Request does not contain an access token",
                    "error": "authorization_required",
                }
            ),401
        )

    @app.before_request
    def create_tables():
        db.create_all()

    api.register_blueprint(ItemBlueprint)
    api.register_blueprint(StoreBlueprint)
    api.register_blueprint(TagBlueprint)
    api.register_blueprint(UserBlueprint)


    return app
