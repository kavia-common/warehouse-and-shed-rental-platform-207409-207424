from flask_smorest import Blueprint
from flask.views import MethodView
from flask import request
from flask_jwt_extended import jwt_required
from app.models import db, Warehouse
from app.schemas import WarehouseSchema
from marshmallow import ValidationError

blp = Blueprint("Warehouses", "warehouses", url_prefix="/warehouses", description="Warehouse and shed routes")

warehouse_schema = WarehouseSchema()
warehouse_list_schema = WarehouseSchema(many=True)

# PUBLIC_INTERFACE
@blp.route("/", methods=["GET"])
class WarehouseList(MethodView):
    """List or search warehouses, supports filter by q, city, type, and availability with pagination."""
    def get(self):
        query = Warehouse.query
        q = request.args.get("q")
        city = request.args.get("city")
        type_ = request.args.get("type")
        avail = request.args.get("available")
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)

        if q:
            query = query.filter(Warehouse.name.ilike(f"%{q}%"))
        if city:
            query = query.filter_by(city=city)
        if type_:
            query = query.filter_by(type=type_)
        if avail is not None:
            val = avail.lower()
            if val in ("1", "true", "yes"):
                query = query.filter_by(is_available=True)
            elif val in ("0", "false", "no"):
                query = query.filter_by(is_available=False)
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)
        results = warehouse_list_schema.dump(paginated.items)
        return {
            "warehouses": results,
            "pagination": {
                "total": paginated.total,
                "pages": paginated.pages,
                "page": paginated.page,
                "per_page": per_page
            }
        }

# PUBLIC_INTERFACE
@blp.route("/<int:warehouse_id>", methods=["GET"])
class WarehouseDetail(MethodView):
    """Get details for a warehouse"""
    def get(self, warehouse_id):
        warehouse = Warehouse.query.get(warehouse_id)
        if not warehouse:
            return {"message": "Warehouse not found"}, 404
        return warehouse_schema.dump(warehouse)

# PUBLIC_INTERFACE
@blp.route("/", methods=["POST"])
class WarehouseCreate(MethodView):
    """Create a new warehouse (protected for demo)"""
    @jwt_required()
    def post(self):
        data = request.get_json()
        try:
            obj = warehouse_schema.load(data)
        except ValidationError as err:
            return {"errors": err.messages}, 400
        warehouse = Warehouse(**obj)
        db.session.add(warehouse)
        db.session.commit()
        return warehouse_schema.dump(warehouse), 201

# PUBLIC_INTERFACE
@blp.route("/<int:warehouse_id>", methods=["PUT", "DELETE"])
class WarehouseEdit(MethodView):
    """Update or delete a warehouse (protected for demo)"""
    @jwt_required()
    def put(self, warehouse_id):
        warehouse = Warehouse.query.get(warehouse_id)
        if not warehouse:
            return {"message": "Warehouse not found"}, 404
        data = request.get_json()
        try:
            obj = warehouse_schema.load(data, partial=True)
        except ValidationError as err:
            return {"errors": err.messages}, 400
        for field, value in obj.items():
            setattr(warehouse, field, value)
        db.session.commit()
        return warehouse_schema.dump(warehouse)

    @jwt_required()
    def delete(self, warehouse_id):
        warehouse = Warehouse.query.get(warehouse_id)
        if not warehouse:
            return {"message": "Warehouse not found"}, 404
        db.session.delete(warehouse)
        db.session.commit()
        return {"message": "Deleted"}
