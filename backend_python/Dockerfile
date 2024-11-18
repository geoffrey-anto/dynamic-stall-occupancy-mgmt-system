FROM python:3.9

WORKDIR /home/app

COPY ./requirements.txt /code/requirements.txt

RUN apt-get update && apt-get install libgl1 -y

RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY . .

EXPOSE 8000

CMD ["fastapi", "run", "main.py", "--port", "8000", "--host", "0.0.0.0", "--reload"]