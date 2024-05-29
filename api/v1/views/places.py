#!/usr/bin/python3
"""Handles all default RESTful API actions on Place objects"""

from flask import jsonify, abort, request
from models import storage
from models.amenity import Amenity
from models.city import City
from models.place import Place
from models.state import State
from models.user import User
from api.v1.views import app_views


@app_views.route('/cities/<city_id>/places', methods=['GET'],
                 strict_slashes=False)
def get_places(city_id):
    """Retrieves the list of all Place objects of a City"""
    city = storage.get(City, city_id)
    if city is None:
        abort(404)

    places = [place.to_dict() for place in city.places]
    return jsonify(places)


@app_views.route('/places/<place_id>', methods=['GET'], strict_slashes=False)
def get_place(place_id):
    """Retrieves a specific Place object by ID"""
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)

    return jsonify(place.to_dict())


@app_views.route('/places/<place_id>', methods=['DELETE'],
                 strict_slashes=False)
def delete_place(place_id):
    """Deletes a specific Place object by ID"""
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)

    storage.delete(place)
    storage.save()
    return jsonify({}), 200


@app_views.route('/cities/<city_id>/places', methods=['POST'],
                 strict_slashes=False)
def create_place(city_id):
    """Creates a new Place object"""
    city = storage.get(City, city_id)
    if city is None:
        abort(404)

    req_json = request.get_json()
    if req_json is None:
        abort(400, 'Not a JSON')

    if 'user_id' not in req_json:
        abort(400, 'Missing user_id')

    user = storage.get(User, req_json['user_id'])
    if user is None:
        abort(404)

    if 'name' not in req_json:
        abort(400, 'Missing name')

    req_json['city_id'] = city_id
    new_place = Place(**req_json)
    new_place.save()
    return jsonify(new_place.to_dict()), 201


@app_views.route('/places/<place_id>', methods=['PUT'], strict_slashes=False)
def update_place(place_id):
    """Updates a specific Place object by ID"""
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)

    req_json = request.get_json()
    if req_json is None:
        abort(400, 'Not a JSON')

    for key, value in req_json.items():
        if key not in ['id', 'user_id', 'city_id', 'created_at', 'updated_at']:
            setattr(place, key, value)

    place.save()
    return jsonify(place.to_dict()), 200


@app_views.route('/places_search', methods=['POST'], strict_slashes=False)
def search_places():
    """Retrieves all Place objects based on JSON request body"""
    if request.content_type != "application/json":
        abort(400, description="Not a JSON")

    places = storage.all(Place).values()
    
    req_json = request.get_json()
    states_ids = req_json.get('states', [])
    cities_ids = req_json.get('cities', [])
    amenities_ids = req_json.get('amenities', [])
    if not req_json or not (states_ids or cities_ids or amenities_ids):
        return jsonify([place.to_dict() for place in places])

    states = [storage.get(State, id) for id in states_ids]
    cities = [storage.get(City, id) for id in cities_ids]

    states = [state for state in states if state]
    cities = [city for city in cities if city]

    states_cities = [city for state in states for city in state.cities]
    req_cities = [city for city in cities if city not in states_cities]
    req_cities.extend(states_cities)

    amenities = [storage.get(Amenity, id) for id in amenities_ids]
    amenities = [amenity for amenity in amenities if amenity]

    req_places = [place for city in req_cities
                  for place in city.places]
    if not req_places:
        req_places = places

    req_places = [place.to_dict() for place in req_places
                  if all(amenity in place.amenities
                         for amenity in amenities)]
    for place in req_places:
        if 'amenities' in place:
            del place['amenities']

    return jsonify(req_places)