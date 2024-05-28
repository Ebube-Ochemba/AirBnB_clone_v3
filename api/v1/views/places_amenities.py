#!/usr/bin/python3
"""
view for the link between Place objects and
Amenity objects that handles all default RESTFul API actions
"""

from flask import jsonify, abort
from api.v1.views import app_views
from models import storage
from models import storage_t
from models.place import Place
from models.amenity import Amenity


@app_views.route('/places/<place_id>/amenities',
                 methods=['GET'], strict_slashes=False)
def get_place_aminities(place_id):
    """Retrieves the list of all Amenity objects of a Place"""

    place = storage.get(Place, place_id)
    if not place:
        abort(404)

    if storage_t == 'db':
        place_aminities = [amenity.to_dict() for amenity in place.amenities]
    else:
        place_aminities = [(storage.get("Amenity", amenity_id).to_dict()
                            for amenity_id in place.amenity_ids)]

    return jsonify(place_aminities)


@app_views.route('/places/<place_id>/amenities/<amenity_id>',
                 methods=['DELETE'], strict_slashes=False)
def delete_place_amenity(place_id, amenity_id):
    """Deletes a Amenity object to a Place"""

    place = storage.get(Place, place_id)
    amenity = storage.get(Amenity, amenity_id)
    if any((not place, not amenity)):
        abort(404)

    if storage_t == 'db':
        if amenity not in place.amenities:
            abort(404)
        else:
            amenity.delete()
            storage.save()
            return jsonify({}), 200
    else:
        if amenity not in place.amenity_ids:
            abort(404)
        else:
            place.amenity_ids.remove(amenity.id)
            storage.save()
            return jsonify({}), 200


@app_views.route('/places/<place_id>/amenities/<amenity_id>',
                 methods=['POST'], strict_slashes=False)
def link_place_amenity(place_id, amenity_id):
    """Link a Amenity object to a Place"""

    place = storage.get(Place, place_id)
    amenity = storage.get(Amenity, amenity_id)
    if not place or not amenity:
        abort(404)

    if storage_t == 'db':
        if amenity in place.amenities:
            return jsonify(amenity.to_dict()), 200
        else:
            place.amenities.append(amenity)
            place.save()
            return jsonify(amenity.to_dict()), 201
    else:
        if amenity.id in place.amenity_ids:
            return jsonify(amenity.to_dict()), 200
        else:
            place.amenity_ids.append(amenity.id)
            place.save()
            return jsonify(amenity.to_dict()), 201
