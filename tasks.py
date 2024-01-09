from celery import Celery
import celeryconfig
from celery import shared_task

import trade_alerts

app = Celery(broker='redis://localhost:6379')

app.config_from_object(celeryconfig)
app.autodiscover_tasks()

@shared_task
def main():
    uri = f"{trade_alerts.request_method} {trade_alerts.request_host}{trade_alerts.request_path}"
    jwt_token = trade_alerts.build_jwt(trade_alerts.service_name, uri)
    orders = trade_alerts.return_orders(jwt_token)
    for order in orders["fills"]:
        order_side = order["side"]
        order_product_id = order["product_id"]
        trade_alerts.send_message(order_side, order_product_id)
