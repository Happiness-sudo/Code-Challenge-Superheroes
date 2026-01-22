from flask import Blueprint, jsonify, request
from .models import Hero, Power, HeroPower
from .extensions import db

api = Blueprint("api", __name__)

# --- HERO ROUTES ---
@api.route("/heroes", methods=["GET"])
def get_heroes():
    heroes = Hero.query.all()
    data = [{"id": h.id, "name": h.name, "super_name": h.super_name} for h in heroes]
    return jsonify(data)

@api.route("/heroes/<int:id>", methods=["GET"])
def get_hero(id):
    hero = Hero.query.get(id)
    if not hero:
        return jsonify({"error": "Hero not found"}), 404
    data = {
        "id": hero.id,
        "name": hero.name,
        "super_name": hero.super_name,
        "hero_powers": [
            {
                "id": hp.id,
                "hero_id": hero.id,
                "power_id": hp.power.id,
                "strength": hp.strength,
                "power": {
                    "id": hp.power.id,
                    "name": hp.power.name,
                    "description": hp.power.description
                }
            } for hp in hero.hero_powers
        ]
    }
    return jsonify(data)

# --- POWER ROUTES ---
@api.route("/powers", methods=["GET"])
def get_powers():
    powers = Power.query.all()
    data = [{"id": p.id, "name": p.name, "description": p.description} for p in powers]
    return jsonify(data)

@api.route("/powers/<int:id>", methods=["GET"])
def get_power(id):
    power = Power.query.get(id)
    if not power:
        return jsonify({"error": "Power not found"}), 404
    return jsonify({"id": power.id, "name": power.name, "description": power.description})

@api.route("/powers/<int:id>", methods=["PATCH"])
def update_power(id):
    power = Power.query.get(id)
    if not power:
        return jsonify({"error": "Power not found"}), 404

    data = request.get_json()
    try:
        power.description = data.get("description", power.description)
        db.session.commit()
        return jsonify({"id": power.id, "name": power.name, "description": power.description})
    except Exception as e:
        db.session.rollback()
        return jsonify({"errors": [str(e)]}), 400

# --- HEROPOWER ROUTES ---
@api.route("/hero_powers", methods=["POST"])
def create_hero_power():
    data = request.get_json()
    try:
        hp = HeroPower(
            hero_id=data["hero_id"],
            power_id=data["power_id"],
            strength=data["strength"]
        )
        db.session.add(hp)
        db.session.commit()
        return jsonify({
            "id": hp.id,
            "hero_id": hp.hero.id,
            "power_id": hp.power.id,
            "strength": hp.strength,
            "hero": {"id": hp.hero.id, "name": hp.hero.name, "super_name": hp.hero.super_name},
            "power": {"id": hp.power.id, "name": hp.power.name, "description": hp.power.description}
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"errors": [str(e)]}), 400
