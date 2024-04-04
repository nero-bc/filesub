FROM python:3.9-alpine

WORKDIR /FSub
COPY . ./

ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PIP_ROOT_USER_ACTION=ignore

RUN pip install --quiet \
pyrogram==2.0.106 \
tgcrypto==1.2.5 \
uvloop==0.19.0 \
pyromod==3.1.6 \
pymongo==4.6.3

CMD ["python", "-m", "FSub"]
