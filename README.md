Médonay
=======

This is a set of microservices to extract metadata from various sources (your
emails, your online accounts) and taking actions on it. Using a microservice
approach has the great advantage of being able to write any parser in the best
fitted language, as is perfectly well described on [this blog
post](https://blog.iamthefij.com/2018/03/08/building-a-self-hosted-email-assistant/).

The core idea is to have a set of interchangeable microservices:
* A set of *crawlers* which are crawling through various places (emails,
  accounts, …) to fetch your data and handing it over to parsers.
* A set of *parsers* to extract metadata from your emails.
* An *indexer* which is basically exposing an API endpoint to store metadata
  extracted from your emails.
* A *viewer* to browse the fetched metadata.

Each microservice could be easily replaced by an alternative microservice. For
instance, the current implementation of the *indexer* uses an SQLite backend,
but you might want to use MongoDB or CouchDB, which is just a matter of
changing the *indexer* component.

Supported crawlers so far are:
- [x] An email crawler to fetch data from your emails. It can either fetch
    automatically over IMAP or read emails you pipe to it.
- [x] A [Web Outside of Browsers](http://weboob.org/) based crawler to fetch
    data from your online accounts (by scraping them). This one is a bit
    particular as Web Outside of Browsers already returns structured data, so
    it does not call any parser under the hood.

Supported extractors (parsers) so far are:

- [x] Extract package tracking info from emails.
- [x] Extract some of [structured metadata](https://developers.google.com/gmail/markup/getting-started):
    - [x] Bus tickets
    - [x] Flight tickets
    - [ ] More to come!
- [x] All the [billing modules](http://weboob.org/applications/boobill) from
    Web Outside of Browsers.
- [x] All the [calendar modules](http://weboob.org/applications/boobcoming)
    from Web Outside of Browsers.

Each microservice accepts environment variables to customize its behavior.
These are `HOST` (for the host to bind to), `PORT` (for the port to bind to)
and `DEBUG` (for enabling or not debug mode). Other environment variables
might be available, have a look at `scripts/run.sh` file.

This repository started as a fork of [iamthefij's
email-assistant](https://git.iamthefij.com/iamthefij/email-assistant), but is
now differing quite a lot.

Detailed documentation and design guides, including guides to extend the
available parsers, are available in [the `doc` folder](doc/).


## Testing it out

Here are some basic steps to get started:

```bash
git clone https://github.com/Phyks/medonay
cd medonay
# Create a virtual env and install all required dependencies. Same for Ruby
# scripts.
./scripts/setup.sh
# Next, start the indexer, parsers and viewer. You can edit the variables at
# the beginning of the file.
./scripts/run.sh
```

Then, for instance, you can easily start parsing emails by `cat`ing them to
the `crawler`:

```bash
cd crawlers/imap-crawler && cat /path/to/email.eml | INDEXER_URL=http://127.0.0.1:4100 PARSER_1=http://127.0.0.1:4001 PARSER_2=http://127.0.0.1:4002 python -m imapCrawler
```

Pass it `INDEXER_TOKEN=<token>` as well if you used a token to protect your
indexer.


**Note about Docker files**: The initial setup was using Docker files and
Docker compose. I'm not using Docker, hence these files are left for
documentation purpose, but not actively maintained. Any contribution to
maintain these Docker files would be greatly appreciated! :)


## License

This repository is licensed under [MIT
license](https://opensource.org/licenses/MIT).
