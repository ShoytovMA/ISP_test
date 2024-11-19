FROM python:3.12.1
COPY ./requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --upgrade -r ./requirements.txt
COPY ./spider.py ./spider.py
COPY ./crawler.py ./crawler.py
CMD ["python", "crawler.py"]