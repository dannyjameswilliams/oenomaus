FROM python:3.10-slim
WORKDIR /app
COPY . .
RUN sh setup.sh
CMD ["python", "bot.py"]
