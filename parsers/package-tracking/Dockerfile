FROM ruby:2.5.0

# TODO: Move to Gemfile
RUN gem install sinatra -v 2.0
RUN gem install tracking_number -v 0.10.3

EXPOSE 3000

RUN mkdir -p /src
WORKDIR /src

COPY main.rb  /src/

CMD ruby main.rb
