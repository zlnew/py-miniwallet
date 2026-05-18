from flask import Blueprint, jsonify, request
from sqlalchemy import select

from app.dto import AccountData, TransactionData
from app.extensions import db
from app.models import Account, Transaction
from app.schema import (
    AccountCreateRequest,
    AccountUpdateRequest,
    TopUpRequest,
    TransactionGetRequest,
    TransferRequest,
)

wallet_bp = Blueprint("wallet", __name__)


@wallet_bp.route("/accounts", methods=["GET"])
def get_accounts():
    accounts = db.session.scalars(select(Account)).all()

    response = [AccountData.model_validate(acc).model_dump() for acc in accounts]

    return jsonify(response), 200


@wallet_bp.route("/accounts/<int:account_id>", methods=["GET"])
def get_account(account_id: int):
    account = db.session.get(Account, account_id)

    if not account:
        return jsonify({"message": "Account not found"}), 404

    response = AccountData.model_validate(account)

    return jsonify(response.model_dump())


@wallet_bp.route("/accounts", methods=["POST"])
def create_account():
    payload: dict[str, str] = request.get_json() or {}
    data = AccountCreateRequest.model_validate(payload)

    new_account = Account(name=data.name, balance=data.balance)

    db.session.add(new_account)
    db.session.commit()

    response = AccountData.model_validate(new_account)

    return jsonify(response.model_dump()), 201


@wallet_bp.route("/accounts/<int:account_id>", methods=["PATCH", "PUT"])
def update_account(account_id: int):
    payload: dict[str, str] = request.get_json() or {}
    data = AccountUpdateRequest.model_validate(payload)

    account = db.session.get(Account, account_id)

    if not account:
        return jsonify({"message": "Account not found"}), 404

    account.name = data.name

    db.session.commit()

    response = AccountData.model_validate(account)

    return jsonify(response.model_dump())


@wallet_bp.route("/transactions", methods=["GET"])
def get_transactions():
    payload: dict[str, str] = request.get_json() or {}
    data = TransactionGetRequest.model_validate(payload)

    transactions = db.session.scalars(
        select(Transaction).where(Transaction.account_id == data.account_id)
    ).all()

    response = [TransactionData.model_validate(tr).model_dump() for tr in transactions]

    return jsonify(response), 200


@wallet_bp.route("/transactions/top-up", methods=["POST"])
def top_up():
    payload: dict[str, str] = request.get_json() or {}
    data = TopUpRequest.model_validate(payload)

    idempotency_key = request.headers.get("X-Idempotency-Key")

    if not idempotency_key:
        return jsonify({"message": "Missing X-Idempotency-Key header"}), 400

    with db.session.begin():
        existing_transaction = db.session.execute(
            select(Transaction).where(Transaction.idempotency_key == idempotency_key)
        ).scalar_one_or_none()

        if existing_transaction:
            account = db.session.get(Account, existing_transaction.account_id)

            response = AccountData.model_validate(account)

            return jsonify(response.model_dump())

        account = db.session.execute(
            select(Account).where(Account.id == data.account_id).with_for_update()
        ).scalar_one_or_none()

        if not account:
            return jsonify({"message": "Account not found"}), 404

        account.balance += data.amount

        transaction = Transaction(
            account_id=account.id,
            type="top_up",
            amount=data.amount,
            idempotency_key=idempotency_key,
        )

        db.session.add(transaction)

    response = AccountData.model_validate(account)

    return jsonify(response.model_dump())


@wallet_bp.route("/transactions/transfer", methods=["POST"])
def transfer():
    payload: dict[str, str] = request.get_json() or {}
    data = TransferRequest.model_validate(payload)

    idempotency_key = request.headers.get("X-Idempotency-Key")

    if not idempotency_key:
        return jsonify({"message": "Missing X-Idempotency-Key header"}), 400

    if data.from_account_id == data.to_account_id:
        return jsonify({"message": "Cannot transfer to same account"}), 400

    with db.session.begin():
        existing_transaction = db.session.execute(
            select(Transaction).where(Transaction.idempotency_key == idempotency_key)
        ).scalar_one_or_none()

        if existing_transaction:
            return jsonify({"message": "Transfer already processed"})

        account_ids = sorted([data.from_account_id, data.to_account_id])

        accounts = (
            db.session.execute(
                select(Account).where(Account.id.in_(account_ids)).with_for_update()
            )
            .scalars()
            .all()
        )

        accounts_map = {account.id: account for account in accounts}

        from_account = accounts_map.get(data.from_account_id)
        to_account = accounts_map.get(data.to_account_id)

        if not from_account or not to_account:
            return jsonify({"message": "Account not found"}), 404

        if from_account.balance < data.amount:
            return jsonify({"message": "Insufficient balance"}), 400

        from_account.balance -= data.amount
        to_account.balance += data.amount

        db.session.add(
            Transaction(
                account_id=from_account.id,
                type="transfer_out",
                amount=data.amount,
                idempotency_key=idempotency_key,
            )
        )

        db.session.add(
            Transaction(
                account_id=to_account.id,
                type="transfer_in",
                amount=data.amount,
            )
        )

    return jsonify({"message": "Transfer successful"})
