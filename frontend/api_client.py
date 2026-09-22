import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


class APIError(Exception):
    pass


def ask_question(question: str, timeout: int = 60) -> dict:
    """يرسل سؤال للـ backend ويرجّع {answer, sources}."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/query",
            json={"question": question},
            timeout=timeout,
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        raise APIError("مش قادر أتواصل مع السيرفر. تأكد إن الـ backend شغال على المنفذ الصحيح.")
    except requests.exceptions.Timeout:
        raise APIError("السيرفر بياخد وقت طويل أكتر من اللازم في الرد. حاول تاني.")
    except requests.exceptions.HTTPError as e:
        raise APIError(f"حصل خطأ من السيرفر: {e.response.status_code}")
    except Exception as e:
        raise APIError(f"حصل خطأ غير متوقع: {str(e)}")


def check_health() -> bool:
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except Exception:
        return False