FROM python:3.10-slim
COPY . ./
RUN pip install -r requirements.txt
RUN chmod +x runbot.sh
CMD ["./runbot.sh"]