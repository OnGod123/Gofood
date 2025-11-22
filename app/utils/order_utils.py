from app.merchant.Database.order import OrderSingle, OrderMultiple
from sqlalchemy import desc

def get_latest_order(session, user_id):
    single = session.query(OrderSingle).filter_by(user_id=user_id).order_by(desc(OrderSingle.created_at)).first()
    multiple = session.query(OrderMultiple).filter_by(user_id=user_id).order_by(desc(OrderMultiple.created_at)).first()

    # Return whichever is newer
    if single and multiple:
        return single if single.created_at > multiple.created_at else multiple
    return single or multiple

