FROM python:slim
RUN apt-get update && apt install -y build-essential

EXPOSE 5432

RUN python3 -m venv venv
RUN . venv/bin/activate
RUN pip install flask web3 flask-cors

WORKDIR /app
CMD ls && bash /app/run.sh

