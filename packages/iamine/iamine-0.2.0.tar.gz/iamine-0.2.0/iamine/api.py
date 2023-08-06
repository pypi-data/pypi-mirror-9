import signal
import asyncio
from getpass import getpass

from .core import Miner
from .config import write_config_file


def get_miner(**kwargs):
    return Miner(**kwargs)


def search(query=None, params=None, callback=None, mine_ids=None, info_only=None,
           **kwargs):
    """Mine Archive.org search results.

    :param query: (optional) The Archive.org search query to yield
                  results for. Refer to https://archive.org/advancedsearch.php#raw
                  for help formatting your query. If no query is given,
                  all indexed items will be mined!
    :type query: str

    :param params: (optional) The URL parameters to send with each
                   request sent to the Archive.org Advancedsearch Api.
    :type params: dict

    :param callback: (optional) A callback function to be called on each
                     :py:class:`aiohttp.client.ClientResponse`.

    :param mine_ids: (optional) By default, ``search`` mines through
                     search results. To mine through the item metadata
                     for each item returned by your query instead, set
                     ``mine_ids`` to ``True``.
    :type mine_ids: bool

    :param info_only: (optional) Set to ``True`` to return information
                      about your query rather than mining any metadata
                      or search results.
    :type info_only: bool

    :param \*\*kwargs: (optional) Arguments that ``get_miner`` takes.
    """
    query = '(*:*)' if not query else query
    params = params if params else {}
    mine_ids = True if mine_ids else False
    info_only = True if info_only else False

    if not kwargs.get('loop'):
        loop = asyncio.get_event_loop()
    else:
        loop = kwargs['loop']
    miner = Miner(loop, **kwargs)

    if info_only:
        params = miner.get_search_params(query, params)
        r = loop.run_until_complete(miner.get_search_info(params))
        search_info = r.get('responseHeader')
        search_info['numFound'] = r.get('response', {}).get('numFound', 0)
        return search_info

    try:
        loop.add_signal_handler(signal.SIGINT, loop.stop)
        loop.run_until_complete(miner.search(query, params=params, callback=callback,
                                             mine_ids=mine_ids))
    except RuntimeError:
        pass


def mine_urls(urls, params=None, callback=None, **kwargs):
    """Concurrently retrieve URLs.

    :param urls: A set of URLs to concurrently retrieve.
    :type urls: iterable

    :param params: (optional) The URL parameters to send with each
                   request.
    :type params: dict

    :param callback: (optional) A callback function to be called on each
                     :py:class:`aiohttp.client.ClientResponse`.

    :param \*\*kwargs: (optional) Arguments that ``get_miner`` takes.
    """
    if not kwargs.get('loop'):
        loop = asyncio.get_event_loop()
    else:
        loop = kwargs['loop']
    miner = get_miner(loop, **kwargs)
    try:
        loop.add_signal_handler(signal.SIGINT, loop.stop)
        loop.run_until_complete(miner.mine_urls(urls, params, callback))
    except RuntimeError:
        pass


def mine_items(identifiers, params=None, callback=None, **kwargs):
    """Concurrently retrieve metadata from Archive.org items.

    :param identifiers: A set of Archive.org item identifiers to mine.
    :type identifiers: iterable

    :param params: (optional) The URL parameters to send with each
                   request.
    :type params: dict

    :param callback: (optional) A callback function to be called on each
                     :py:class:`aiohttp.client.ClientResponse`.

    :param \*\*kwargs: (optional) Arguments that ``get_miner`` takes.
    """
    if not kwargs.get('loop'):
        loop = asyncio.get_event_loop()
    else:
        loop = kwargs['loop']
    miner = Miner(loop, **kwargs)
    try:
        loop.add_signal_handler(signal.SIGINT, loop.stop)
        loop.run_until_complete(miner.mine_items(identifiers, params, callback))
    except RuntimeError:
        pass


def configure(username=None, password=None, overwrite=None):
    """Configure IA Mine with your Archive.org credentials."""
    username = input('Email address: ') if not username else username
    password = getpass('Password: ') if not password else password
    write_config_file(username, password, overwrite)
