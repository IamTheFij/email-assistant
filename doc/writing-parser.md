Writing a new parser
====================

You can write a new parser in any language of your choice. Some existing
parsers are available in the `parsers` directory at the root of this
repository. Simply put your new parser there and update the scripts in
`scripts/` accordingly. Then, you can just add its URL to the `PARSERS`
(an ordered comma-separated list of parsers to call) environement variable
passed to the `crawler`.

Your parser should just respect the following specification.


## Standardized web API

When parsing an email, the system will call the parsers through their `/parse`
endpoint. The payload is a JSON-encoded dictionary with the following
structure:

```
{
    "subject": "THE SUBJECT OF THE EMAIL",
    "message": {
        "plain": "THE CONTENT OF THE EMAIL AS PLAINTEXT",
        "html": "THE HTML CONTENT OF THE EMAIL"
    }
}
```

Your parser should return a JSON-encoded list of dictionaries for each
metadata extracted from the email. Each dictionary should have the following
structure:

```
{
    "token": "A UNIQUE TOKEN",
    "type": "TYPE OF THE EXTRACTED METADATA",
    "METADATA": "ANY PAYLOAD CONTAINING THE DETAILS OF THE METADATA"
}
```

The `token` should be unique as the `indexer` will use it to prevent a
reimport. It can typically be a tracking number for parcel delivery, a ticket
number for ticketing, etc.

The `type` is the type of metadata extracted with your parser. As many emails
follow some [schema.org](http://schema.org/) standardization of types, please
consider using these schemas whenever possible, to standardize the output of
parsers and increase reusability. Typically, the `type` for a parcel tracking
should be `ParcelDelivery` and follow
[http://schema.org/ParcelDelivery](http://schema.org/ParcelDelivery).

The returned payload will get added to the `indexer`.

*Note*: Your parsers are not bound to call the indexer. If they return
anything, it will be pushed to the `indexer` but a parser could also simply
call some external service according to the payload, to add `ical` events to
your calendar for instance.
