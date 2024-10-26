FROM python:3.9

WORKDIR /home/app

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./ /home/app

EXPOSE 8000

CMD ["fastapi", "run", "main.py", "--port", "8000", "--host", "0.0.0.0", "--reload"]