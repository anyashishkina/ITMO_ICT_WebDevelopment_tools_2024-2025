from celery import Celery
import requests

celery_app = Celery(
    "worker",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0"
)

@celery_app.task
def parse_url_task(url: str) -> dict:
    import requests
    try:
        response = requests.get(url)
        response.raise_for_status()
        html = response.text
        return {"message": "Parsing completed", "content_length": len(html)}
    except Exception as e:
        return {"error": str(e)}