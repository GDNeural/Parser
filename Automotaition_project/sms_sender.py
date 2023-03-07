import json
import os
import requests

from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)


class SigmaSMS:

    @classmethod
    def send_message(cls, recipient: str, text: str):
        try:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': os.environ['SIGMASMS_TOKEN']
            }
            payload = {
                'recipient': recipient,
                'type': 'sms',
                "payload": {
                    'sender': os.environ['SIGMASMS_SENDER'],
                    'text': text
                }
            }
            response = requests.request("POST", os.environ['SIGMASMS_URL'], headers=headers, data=json.dumps(payload),
                                        timeout=5)
            return response.status_code, response.json()
        except Exception as e:
            print(str(e))
