FROM python:3.6-onbuild

# ENV FLASK_APP=indexer/app.py
ENV FLASK_DEBUG=1

EXPOSE 5000

# TODO: Track debug in env and use threads
CMD python -m indexer.main
