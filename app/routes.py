from flask import Blueprint, jsonify, request

from app.dto import AccountData
from app.extensions import db
from app.models import Account
from app.schema import AccountSaveRequest

wallet_bp = Blueprint("wallet", __name__)


@wallet_bp.route("/accounts", methods=["POST"])
def create_account():
    payload: dict[str, str] = request.get_json() or {}
    data = AccountSaveRequest.model_validate(payload)

    new_account = Account(name=data.name, balance=data.balance)

    db.session.add(new_account)
    db.session.commit()

    response = AccountData.model_validate(new_account)

    return jsonify(response.model_dump()), 201


@wallet_bp.route("/accounts/<int:account_id>", methods=["PATCH", "PUT"])
def update_account(account_id: int):
    payload: dict[str, str] = request.get_json() or {}
    data = AccountSaveRequest.model_validate(payload)

    account = db.session.get(Account, account_id)

    if not account:
        return jsonify({"message": "Account not found"}), 404

    account.name = data.name
    account.balance = data.balance

    db.session.commit()

    response = AccountData.model_validate(account)

    return jsonify(response.model_dump())


@wallet_bp.route("/accounts/<int:account_id>", methods=["GET"])
def get_account(account_id: int):
    account = db.session.get(Account, account_id)

    if not account:
        return jsonify({"message": "Account not found"}), 404

    response = AccountData.model_validate(account)

    return jsonify(response.model_dump())


@wallet_bp.route("/transactions/top-up", methods=["POST"])
def top_up():
    return jsonify({})


@wallet_bp.route("/transactions/transfer", methods=["POST"])
def transfer():
    return jsonify({})
