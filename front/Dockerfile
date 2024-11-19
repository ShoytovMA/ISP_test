FROM python:3.12.1
COPY ./requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --upgrade -r ./requirements.txt
COPY ./app.py ./app.py
CMD ["fastapi", "run", "app.py", "--port", "80"]