FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN useradd --create-home demo && mkdir -p var && chown -R demo:demo /app
USER demo
EXPOSE 8002
CMD ["python", "run.py", "--host", "0.0.0.0"]
