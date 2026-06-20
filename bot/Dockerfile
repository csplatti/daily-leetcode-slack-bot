FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

ENV PORT=5001

EXPOSE 5001

# below is written by claude. TODO: understand it.
CMD ["python3", "app.py"]