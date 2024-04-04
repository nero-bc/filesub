FROM python:3.9-alpine

WORKDIR /FSub
COPY . ./

ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PIP_ROOT_USER_ACTION=ignore

RUN pip install --quiet pyrogram tgcrypto uvloop pyromod pymongo

CMD ["python", "-m", "FSub"]
