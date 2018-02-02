# Email Parser Design

## Purpose
A service that can read emails from an IMAP inbox and extract data and send it to other services

## Functionality
 * Extract tracking numbers and send to a package tracking service
 * Extract flight numbers and confirmations and send to trip tracking service
 * Extract dates and events and send to a calendar service

## Secondary services

### Package Tracking service
 * Receive tracking info via API and store in database
 * Web interface for viewing current status of all packages
 * Filters by date and status
 * ical subscription for arrival dates

### Flight Tracking Service
 * Receive tracking info via API and store in database
 * Web interface for viewing current status of all flights
 * Filters by date and status
 * ical subscription for flight times

## Architecture 1: Micro-services
A single service to read email content and send the email content to a list of parser services.

A parser service would conform to an interface with an API that accepts an email with several attributes: sender, recipients, subject, body, datetime. It would then extract some attribute and send it to a tracking service. The attribute would be something like the tracking number for a flight or package and a calender time for an event.

A tracking service would accept this info and store in it's database. It would then provide a front end to this data via a website and an ical calendar URL. It may also be possible to abstract further the schemas and interface such that all trackers share a common infrastructure but make unique requests to metadata services.

## Architecture 2: Micro-services

Scanner service to scan emails and send to indexer. Indexer receives the email contents and makes requests to the parser services. Parser services respond with extracted text and the indexer will insert them into the database. The indexer also exposes a restful api on top of the data model.

Viewing services would use the restful API to display content and expose additional metadata.

## Architecture 3: Message based queue

Scanner scans emails and inserts task into a queuing service (RabbitMQ with a fanout). Multiple parsers read from these queues and attach extracted data and make requests to the indexing service for storage. Front end services sit on top of a restful api on the database.

## Useful packages
Golang package for extracting numbers and carriers from unstructured text: https://github.com/lensrentals/trackr

Python package for retrieving status from a tracking number: https://github.com/alertedsnake/packagetracker

Ruby gem for extracting shipping info from a number or unstructured text: https://github.com/jkeen/tracking_number

Ruby gem for retrieving tracking info based on an ID: https://github.com/travishaynes/trackerific
