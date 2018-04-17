from weboobCrawler.capabilities import CapDocument
from weboobCrawler.capabilities import CapCalendarEvent

SUPPORTED_CAPS = {
    'CapDocument': CapDocument.fetch,
    'CapCalendarEvent': CapCalendarEvent.fetch,
}
