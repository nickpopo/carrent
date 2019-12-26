from flask import jsonify, request
from app.models import Car
from . import bp


# Get car's data.
@bp.route('/cars/<int:id>', methods=['GET'])
def get_car(id):
	return jsonify(Car.query.get_or_404(id).to_dict())