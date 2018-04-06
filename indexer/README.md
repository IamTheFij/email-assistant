# Indexer
Simple service to act as data layer for Email Assitant

## Healthcheck
Path: `/`
Returns: `OK`

## Tokens
Path: `/token`

### POST
Accepts JSON representation of a EmailToken

Accepts:

|Field|Type|Example|
|---|---|---|
|`"subject"`|String|`"Your shipping info"`|
|`"token"`|String|`"123456"`|
|`"type"`|String|`"ParcelDelivery"`|
|`"metadata"`|Object (optional)|`{"carrier": "UPS"}`|
|`"disabled"`|Boolean (optional)|`false`|

Returns:

|Field|Type|Example|
|---|---|---|
|`"success"`|Boolean|`true`|
|`"token"`|Token Object|`{"id": 1, ... }`|

### GET
Path: `/token`
Returns all Token Objects

Parameters:

|Parameter|Description|Example|
|---|---|---|
|`"filter_type"`|String token type to filter by|`SHIPPING`|

Returns:

|Field|Type|Example|
|---|---|---|
|`"tokens"`|List of Token Objects|`[{"id": 1, ... }, ...]`|

Path: `/token/<int:token_id>`
Returns Token Object with that ID
