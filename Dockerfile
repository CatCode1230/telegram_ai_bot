FROM nvidia/cuda:11.8.0-runtime-ubuntu22.04

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip


RUN apt-get update \
    && apt-get install -y git 




COPY requirements.txt ./requirements.txt

RUN python3 -m pip install -r requirements.txt


WORKDIR /app

CMD ["python3", "-u", "__main__.py"]
