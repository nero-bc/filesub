FROM python:3.9-alpine

WORKDIR /FSub
COPY . ./

ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PIP_ROOT_USER_ACTION=ignore

RUN pip install -r requirements.txt

CMD ["python", "-m", "FSub"]