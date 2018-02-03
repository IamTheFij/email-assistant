# parsers

A parser should conform to a simple API spec so that it can be easily accessed

# Healthcheck
Simple endpoint that accepts nothing and returns 'OK' on success.

|Attrs   |   |
|--------|---|
|Path    |`/`|
|Method  |`GET`|
|Response|`"OK"`|
# Parse
The primary endpoint that will parse a message

|Attrs   |   |
|--------|---|
|Path    |`/parse`|
|Method  |`POST`|
|Request |`json`|
|Response|`json`|

Request:

|Key     |Example Value                                        |Description|
|--------|-----------------------------------------------------|-----------|
|`"message"`|`"Here's your tracking number: 1Z879E930346834440"`|Full contents of the email message|
|`"subject"`|`"Your email is here"`|Full contents of the email message|

Response:

|Key         |Example Value         |Description|
|------------|----------------------|-----------|
|`"token"`   |`"1Z879E930346834440"`|String token that was extracted|
|`"type"`    |`"SHIPPING"`          |A string that indicates what type of metadata that was extracted. This will be used by other services to understand what kind of data this is.|
|`"metadata"`|`{"carrier": "UPS"}`  |A dictionary with any other additional metadat that may be used by other services|
