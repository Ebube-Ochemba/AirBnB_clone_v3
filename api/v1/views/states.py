#!/usr/bin/python3
"""
a new view for State objects that handles
all default RESTFul API actions
"""

from flask import jsonify, abort, request
from models.state import State
from api.v1.views import app_views
from models import storage


@app_views.route('/states', methods=['GET'], strict_slashes=False)
def get_states():
    """Retrieves the list of all State objects"""
    all_states = storage.all(State).values()
    states_list = []
    for state in all_states:
        states_list.append(state.to_dict())
    return jsonify(states_list)


@app_views.route('/states/<state_id>', methods=['GET'], strict_slashes=False)
def get_state(state_id):
    """Retrieves a State object"""
    state_obj = storage.get(State, state_id)
    if state_obj is None:
        abort(404)
    return jsonify(state_obj.to_dict())


@app_views.route('/states/<state_id>', methods=['GET'], strict_slashes=False)
def delete_state(state_id):
    """Deletes a State object"""
    state_obj = storage.get(State, state_id)
    if state_obj is None:
        abort(404)
    storage.delete(state_obj)
    storage.save()
    return jsonify({}), 200


@app_views.route('/states', methods=['POST'], strict_slashes=False)
def create_state():
    """Creates a state"""
    data = request.get_json()
    if not data:
        abort(400, description="Not a JSON")
    if 'name' not in data:
        abort(400, description="Missing name")

    new_state = State(**data)
    new_state.save()
    return jsonify(new_state.to_dict()), 201


@app_views.route('/states/<state_id>', methods=['PUT'], strict_slashes=False)
def update_state(state_id):
    """Updates a state object"""
    data = request.get_json()
    state_obj = storage.get(State, state_id)
    if state_obj is None:
        abort(404)
    if not data:
        abort(400, description="Not a JSON")

    for key, value in data.items():
        if key not in ['id', 'created_at', 'updated_at']:
            setattr(state_obj, key, value)
    state_obj.save()
    return jsonify(state_obj.to_dict()), 200
