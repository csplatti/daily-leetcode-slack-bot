FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

ENV PORT=8000

EXPOSE 8000

# below is written by claude. TODO: understand it.
CMD ["fastapi", "run", "main.py", "--host", "0.0.0.0", "--port", "8000"]