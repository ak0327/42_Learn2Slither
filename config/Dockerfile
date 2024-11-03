FROM python:3.10-slim

RUN apt-get update

WORKDIR /app

COPY config/requirements.txt /app/requirements.txt

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt

COPY config/jupyter_notebook_config.py /root/.jupyter/jupyter_notebook_config.py

CMD ["sh"]
