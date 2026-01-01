import requests

def send_discord(webhook: str, content: str):
    requests.post(webhook, json={"content": content}, timeout=10)
