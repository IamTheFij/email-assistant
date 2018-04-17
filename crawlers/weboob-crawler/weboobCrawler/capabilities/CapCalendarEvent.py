"""
Implementation of fetching through the Weboob ``CapCalendarEvent`` capability.
This fetches for events.

Serializes everything to schema.org schemas.
"""
import datetime
import logging

from weboob.capabilities.base import empty

LOGGER = logging.getLogger(__name__)


def fetch_events(weboob_proxy, backend):
    """
    Fetch events from a given backend.

    :param weboob_proxy: an instance of ``weboobproxy`` class.
    :param backend: a valid built backend to use.
    :return the list of fetched events (weboob objects).
    """
    events = []
    for event in backend.list_events(datetime.date(1970, 1, 1)):
        event.id = weboob_proxy._ensure_fully_qualified_id(
            event.id,
            backend
        )
        events.append(event)
    return events


def serialize_event(event):
    """
    Serialization of Weboob ``BaseCalendarEvent`` object to schema.org
    representation.

    :param event: The Weboob ``BaseCalendarEvent`` object to serialize.
    """
    serialized = {
        '@type': 'Event',
        '@context': 'http://schema.org/',
        'identifier': event.id,
        'about': event.summary,
        'description': event.description,
    }

    if event.start_date:
        serialized['startDate'] = event.start_date
    if event.end_date:
        serialized['endDate'] = event.end_date
    if event.start_date and event.end_date:
        serialized['duration'] = event.end_date - event.start_date

    location = ''
    if event.location:
        location = event.location
    if event.city:
        location += ' %s' % (event.city)
    if location:
        event.location = {
            '@type': 'Place',
            'description': location.strip()
        }

    if event.event_planner:
        serialized['organizer'] = {
            '@type': 'Organization',
            'name': event.event_planner,
        }

    if not empty(event.price):
        serialized['isAccessibleForFree'] = (event.price == 0)
        serialized['offers'] = {
            '@type': 'Offer',
            'price': event.price,
        }

    if not empty(event.status):
        if event.status == 'CONFIRMED':
            serialized['eventStatus'] = 'EventScheduled'
        elif event.status == 'CANCELLED':
            serialized['eventStatus'] = 'EventCancelled'


def fetch(weboob_proxy, backend):
    """
    Fetch and serialized data from a ``CapCalendarEvent`` enabled backend.

    :param weboob_proxy: An instance of ``WeboobProxy`` class.
    :param backend: A valid built backend to use.
    :returns: A list of schema.org serialized items to index.
    """
    LOGGER.info('Fetching data...')

    # Fetch all events from 1st of January of 1970
    events = fetch_events(weboob_proxy, backend)
    LOGGER.info('Found events %s.', [x.id for x in events])

    serialized = []
    for event in events:
        serialized.append(serialize_event(event))
    return serialized
