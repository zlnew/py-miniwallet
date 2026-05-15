from decimal import Decimal

from flask import Blueprint, jsonify, request

from app.extensions import db
from app.models import Account

wallet_bp = Blueprint("wallet", __name__)


@wallet_bp.route("/accounts", methods=["POST"])
def create_account():
    data: dict[str, str] = request.get_json(force=True, silent=True) or {}

    if "name" not in data:
        return jsonify({"error": "Name is required"}), 400

    initial_balance = Decimal(str(data.get("balance", 0)))

    new_account = Account(name=data["name"], balance=initial_balance)

    db.session.add(new_account)
    db.session.commit()

    return jsonify(
        {
            "id": new_account.id,
            "name": new_account.name,
            "balance": float(new_account.balance),
        }
    ), 201


@wallet_bp.route("/accounts/<int:account_id>", methods=["GET"])
def get_account(account_id: int):
    account = db.session.get(Account, account_id)

    if not account:
        return jsonify({"error": "Account not found"}), 404

    return jsonify(
        {"id": account.id, "name": account.name, "balance": float(account.balance)}
    )
