import jwt
from cryptography.hazmat.primitives import serialization
import time
import secrets
import http.client
from datetime import datetime, timedelta
import smtplib
import json
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(dotenv_path=Path(".") / ".env")

key_name       = os.environ.get("CB_KEY_NAME")
key_secret     = os.environ.get("CB_KEY_SECRET")
request_method = "GET"
request_host   = "api.coinbase.com"
request_path   = "/api/v3/brokerage/orders/historical/fills"
service_name   = "retail_rest_api_proxy"

def build_jwt(service, uri):
    private_key_bytes = key_secret.encode('utf-8')
    private_key = serialization.load_pem_private_key(private_key_bytes, password=None)
    jwt_payload = {
        'sub': key_name,
        'iss': "coinbase-cloud",
        'nbf': int(time.time()),
        'exp': int(time.time()) + 60,
        'aud': [service],
        'uri': uri,
    }
    jwt_token = jwt.encode(
        jwt_payload,
        private_key,
        algorithm='ES256',
        headers={'kid': key_name, 'nonce': secrets.token_hex()},
    )
    return jwt_token

def return_orders(jwt_token):
    conn = http.client.HTTPSConnection("api.coinbase.com")
    payload = ''
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f"Bearer {jwt_token}"
    }
    now = datetime.utcnow()
    start_sequence_timestamp = (now - timedelta(minutes=1)).strftime('%Y-%m-%dT%H:%M:%SZ')
    conn.request("GET", f"/api/v3/brokerage/orders/historical/fills?start_sequence_timestamp={start_sequence_timestamp}", payload, headers)
    res = conn.getresponse()
    data = res.read()
    return json.loads(data.decode("utf-8"))

def send_message(side, product_id):
    recipient = os.environ.get("MESSAGE_RECIPIENT")
 
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(os.environ.get("GMAIL_EMAIL"), os.environ.get("GMAIL_APP_PASSWORD"))
 
    server.sendmail(os.environ.get("GMAIL_EMAIL"), recipient, f"{side} - {product_id}")


def main():
    while True:
        print("BEGIN REQUEST")
        uri = f"{request_method} {request_host}{request_path}"
        jwt_token = build_jwt(service_name, uri)
        orders = return_orders(jwt_token)
        for order in orders["fills"]:
            order_side = order["side"]
            order_product_id = order["product_id"]
            send_message(order_side, order_product_id)
        time.sleep(60)

main()
