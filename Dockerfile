FROM python:3.8.13
COPY bot.py animekiller.py requirements.txt mytoken.py model resources/laughing_gladiators.gif saved_messages.txt gifmaker.py resources/whip.gif ./
RUN pip install -r requirements.txt
CMD ["python", "bot.py"]