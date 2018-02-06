FROM python:3.6-onbuild

RUN mkdir -p /config
VOLUME /config

ENV SQLALCHEMY_DATABASE_URI sqlite:////config/tokens.db
ENV FLASK_DEBUG=1

EXPOSE 5000

# TODO: Track debug in env and use threads
CMD python -m indexer.main
