from flask_smorest import Blueprint
from flask.views import MethodView
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db, RentalRequest, Warehouse
from app.schemas import RentalRequestSchema
from marshmallow import ValidationError

blp = Blueprint("Rentals", "rentals", url_prefix="/rentals", description="Warehouse rental requests")

rental_schema = RentalRequestSchema()
rental_list_schema = RentalRequestSchema(many=True)

# PUBLIC_INTERFACE
@blp.route("/", methods=["POST"])
class RentalRequestCreate(MethodView):
    """Create a rental request (protected)"""
    @jwt_required()
    def post(self):
        data = request.get_json()
        try:
            user_id = get_jwt_identity()
            data["user_id"] = user_id
            req_obj = rental_schema.load(data)
        except ValidationError as err:
            return {"errors": err.messages}, 400
        # Basic check: warehouse exists
        warehouse = Warehouse.query.get(req_obj['warehouse_id'])
        if not warehouse:
            return {"message": "Warehouse not found"}, 404
        rental = RentalRequest(**req_obj)
        db.session.add(rental)
        db.session.commit()
        return rental_schema.dump(rental), 201

# PUBLIC_INTERFACE
@blp.route("/", methods=["GET"])
class RentalRequestList(MethodView):
    """List user's rental requests (protected)"""
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        query = RentalRequest.query.filter_by(user_id=user_id).order_by(RentalRequest.created_at.desc())
        return {"rental_requests": rental_list_schema.dump(query.all())}

# PUBLIC_INTERFACE
@blp.route("/<int:rental_id>", methods=["GET"])
class RentalRequestDetail(MethodView):
    """Get details of a rental request (owner or requester only)"""
    @jwt_required()
    def get(self, rental_id):
        user_id = get_jwt_identity()
        rental = RentalRequest.query.get(rental_id)
        if not rental or (rental.user_id != user_id and (not rental.warehouse or rental.warehouse.owner_id != user_id)):
            return {"message": "Rental request not found or not allowed"}, 403
        return rental_schema.dump(rental)
