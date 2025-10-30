from flask import Flask
from app.extensions import db, migrate, socketio, oauth, r


def create_app(config_name=None):
    """
    Factory to create and configure the Flask app.
    """
    app = Flask(__name__, static_folder="../static", template_folder="../templates")
    app.config.from_object("config.Config")

    # --- Initialize extensions ---
    db.init_app(app)
    migrate.init_app(app, db)
    socketio.init_app(app, cors_allowed_origins="*")
    oauth.init_app(app)

    # --- Import and register Blueprints ---
    from app.handlers.home import home_bp
    from app.handlers.auth import auth_bp
    from app.handlers.auth_signin import signup_bp  
    from app.handlers.routes import auth_phone
    from app.merchants.handlers import activate_vendor
    from app.merchants.handlers.register_vendor import register_vendor_bp
    from app.merchants.handlers.order_handler import order_bp
    from app.merchants.handlers.notification_handler import notification_bp
    from app.handlers.vendor_dashboard import vendor_bp
    from app.merchants.handlers.search_handler import product_search_bp
    from app.handlers.payment_wall import wallet_payment_bp
    from app.handlers.store_handler import store_bp
    from app.merchants.handlers.wishlist_handler import wishlist_bp
    from app.merchants.handlers.vendor_status_handler import vendor_status_bp
    from app.websocket import delivery_socket
    from app.handlers import moniepoint
    from app.websocket.bargain_namespace import BargainNamespace
    from app.websocket.delivery_namespace import DeliveryNamespace



    app.register_blueprint(home_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(signup_bp)
    app.register_blueprint(auth_phone)
    app.register_blueprint(activate_vendor)
    app.register_blueprint(register_vendor_bp)
    app.register_blueprint(order_bp)
    app.register_blueprint(notification_bp)
    app.register_blueprint(vendor_bp)
    app.register_blueprint(product_search_bp)
    app.register_blueprint(wallet_payment_bp)
    app.register_blueprint(store_bp)
    app.register_blueprint(wishlist_bp) 
    app.register_blueprint(vendor_status_bp)
    app.register_blueprint(moniepoint.monie_bp)
    socketio.on_namespace(BargainNamespace("/bargain"))
    socketio.on_namespace(DeliveryNamespace("/delivery"))


    

    # --- Health Check ---
    @app.route("/health")
    def health():
        return {"status": "ok"}

    @app.route("/cdn-cgi/<path:path>", methods=["GET", "POST"])
    def cdn_ignore(path):
        return "", 204

    return app


