FROM ruby:2.5.0

# TODO: Move to Gemfile
RUN gem install tracking_number -v 1.0.3
RUN gem install sinatra -v 2.0

EXPOSE 3000

RUN mkdir -p /src
WORKDIR /src

COPY main.rb  /src/

CMD ruby main.rb
