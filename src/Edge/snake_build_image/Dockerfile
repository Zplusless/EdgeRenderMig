FROM python:3.7.12-slim

ENV DEBIAN_FRONTEND=noninteractive

COPY sources.list /etc/apt/sources.list

RUN  \ 
  apt-get update && apt-get install -yq python3-pygame\
  && pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple \
  && pip install --no-cache-dir  pygame websockets\
  && apt-get -qq autoremove \
  && apt-get -qq clean \
  && rm -rf /var/lib/apt/lists/* \
  && rm -rf ~/.cache/pip

ENTRYPOINT [ "/bin/bash", "-l", "-c" ]