FROM ruby:2.5.0

# TODO: Move to Gemfile
RUN gem install trackerific -v 0.8.0
RUN gem install sinatra -v 2.0

EXPOSE 3000

RUN mkdir -p /src
WORKDIR /src

COPY main.rb  /src/

CMD ruby main.rb
