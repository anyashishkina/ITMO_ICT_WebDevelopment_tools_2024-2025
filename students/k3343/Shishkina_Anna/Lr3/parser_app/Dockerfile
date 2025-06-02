FROM python:3.11

WORKDIR /parser_app

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . .

CMD ["uvicorn", "parser_app:app", "--host", "0.0.0.0", "--port", "8001"]