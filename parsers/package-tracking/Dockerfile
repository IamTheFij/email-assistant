FROM ruby:2.5.0

RUN mkdir -p /src
WORKDIR /src

EXPOSE 3000

COPY Gemfile /src/
COPY Gemfile.lock /src/
RUN bundle install

COPY main.rb  /src/

CMD ruby main.rb
