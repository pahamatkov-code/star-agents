@router.get("/balance", dependencies=[Depends(require_role("admin"))])
def balance_analytics(
    db: Session = Depends(get_db),
    date_from: datetime | None = Query(None),
    date_to: datetime | None = Query(None),
    user_id: int | None = Query(None),
    type: str | None = Query(None, regex="^(topup|spend)$"),
):
    filters = []

    if date_from:
        filters.append(BalanceTransaction.created_at >= date_from)
    if date_to:
        filters.append(BalanceTransaction.created_at <= date_to)
    if user_id:
        filters.append(BalanceTransaction.user_id == user_id)
    if type:
        filters.append(BalanceTransaction.type == type)

    # Загальні метрики
    total_topups = (
        db.query(func.sum(BalanceTransaction.amount))
        .filter(BalanceTransaction.type == "topup", *filters)
        .scalar() or 0
    )

    total_spent = (
        db.query(func.sum(BalanceTransaction.amount))
        .filter(BalanceTransaction.type == "spend", *filters)
        .scalar() or 0
    )

    net_flow = total_topups + total_spent

    # Графіки
    topups_by_day = (
        db.query(
            func.date(BalanceTransaction.created_at).label("date"),
            func.sum(BalanceTransaction.amount).label("amount")
        )
        .filter(BalanceTransaction.type == "topup", *filters)
        .group_by(func.date(BalanceTransaction.created_at))
        .order_by(func.date(BalanceTransaction.created_at))
        .all()
    )

    spent_by_day = (
        db.query(
            func.date(BalanceTransaction.created_at).label("date"),
            func.sum(BalanceTransaction.amount).label("amount")
        )
        .filter(BalanceTransaction.type == "spend", *filters)
        .group_by(func.date(BalanceTransaction.created_at))
        .order_by(func.date(BalanceTransaction.created_at))
        .all()
    )

    return {
        "filters": {
            "date_from": date_from,
            "date_to": date_to,
            "user_id": user_id,
            "type": type,
        },
        "summary": {
            "total_topups": total_topups,
            "total_spent": abs(total_spent),
            "net_flow": net_flow,
        },
        "topups_by_day": [
            {"date": str(row.date), "amount": row.amount}
            for row in topups_by_day
        ],
        "spent_by_day": [
            {"date": str(row.date), "amount": abs(row.amount)}
            for row in spent_by_day
        ],
    }
