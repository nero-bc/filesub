FROM python:3.11-alpine

RUN apk add git

WORKDIR /FSub
COPY . ./

ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PIP_ROOT_USER_ACTION=ignore

RUN pip install -Ur requirements.txt

CMD ["python", "-m", "bot"]