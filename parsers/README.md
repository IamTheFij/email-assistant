# Parsers

A parser should conform to a simple API spec so that it can be easily
accessed. It is usually called by a crawler to extract meaningful informations
from text.

## Healthcheck

Simple endpoint that accepts nothing and returns 'OK' on success.

|Attrs   |   |
|--------|---|
|Path    |`/`|
|Method  |`GET`|
|Response|`"OK"`|

## Parse

The primary endpoint that will parse a message.

|Attrs   |   |
|--------|---|
|Path    |`/parse`|
|Method  |`POST`|
|Request |`json`|
|Response|`json`|

Request:

|Key     |Example Value                                        |Description|
|--------|-----------------------------------------------------|-----------|
|`"message"`|`{"html": "<p>Here's your tracking number: <a href="">1Z879E930346834440</a></p>", "plain": "Here's your tracking number: 1Z879E930346834440"}`|Dictionary containing the full content of the message as HTML and as plaintext|
|`"subject"`|`"Your tracking infos"`|Subject of an email|
|`"from"`   |`"no-reply@example.com"`|From address of an email|

Response:

|Key         |Example Value         |Description|
|------------|----------------------|-----------|
|`"token"`   |`"1Z879E930346834440"`|String token that was extracted|
|`"type"`    |`"ParcelDelivery"`          |A string that indicates what type of metadata was extracted ([schema.org](http://schema.org/) type). This will be used by other services to understand what kind of data this is.|
|`"metadata"`|`{"trackingNumber": "1Z879E930346834440"}`  |A dictionary with any other additional metadata that may be used by other services. This should conform to the [schema.org](http://schema.org/) type.|
