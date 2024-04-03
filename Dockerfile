FROM python:3.9-alpine

RUN apk add git -q

WORKDIR /fsub
COPY . ./

ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PIP_ROOT_USER_ACTION=ignore

RUN pip install -qr requirements.txt

CMD ["python", "-m", "bot"]