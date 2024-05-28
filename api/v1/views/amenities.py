#!/usr/bin/python3
"""Handles all default RESTFul API actions on Amenity objects"""

from flask import jsonify, abort, request
from models import storage
from models.amenity import Amenity
from api.v1.views import app_views


@app_views.route('/amenities', methods=['GET'], strict_slashes=False)
def get_amenities():
    """Retrieves the list of all Amenity objects"""
    amenities = [amenity.to_dict()
                 for amenity in storage.all(Amenity).values()]

    return jsonify(amenities)


@app_views.route('/amenities/<amenity_id>', methods=['GET'],
                 strict_slashes=False)
def get_amenity(amenity_id):
    """Retrieves a specific Amenity object by ID"""
    amenity = storage.get(Amenity, amenity_id)
    if amenity is None:
        abort(404)

    return jsonify(amenity.to_dict())


@app_views.route('/amenities/<amenity_id>', methods=['DELETE'],
                 strict_slashes=False)
def delete_amenity(amenity_id):
    """Deletes a specific Amenity object by ID"""
    amenity = storage.get(Amenity, amenity_id)
    if amenity is None:
        abort(404)

    storage.delete(amenity)
    storage.save()
    return jsonify({}), 200


@app_views.route('/amenities', methods=['POST'], strict_slashes=False)
def create_amenity():
    """Creates a new Amenity object"""
    try:
        req_json = request.get_json()
    except Exception:
        abort(400, description="Not a JSON")

    if 'name' not in req_json:
        abort(400, 'Missing name')

    new_amenity = Amenity(**req_json)
    new_amenity.save()
    return jsonify(new_amenity.to_dict()), 201


@app_views.route('/amenities/<amenity_id>', methods=['PUT'],
                 strict_slashes=False)
def update_amenity(amenity_id):
    """Updates a specific Amenity object by ID"""
    if request.content_type != "application/json":
        abort(400, description="Not a JSON")

    req_json = request.get_json()
    if req_json is None:
        abort(400, 'Not a JSON')
    
    amenity = storage.get(Amenity, amenity_id)
    if amenity is None:
        abort(404)

    for key, value in req_json.items():
        if key not in ['id', 'created_at', 'updated_at']:
            setattr(amenity, key, value)
    amenity.save()

    return jsonify(amenity.to_dict()), 200
