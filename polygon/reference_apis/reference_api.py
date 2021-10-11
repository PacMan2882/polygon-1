# ========================================================= #
import requests
import httpx
from typing import Union
import datetime
from requests.models import Response
from httpx import Response as HttpxResponse
# ========================================================= #


class ReferenceClient:
    """
    These docs are not meant for general users. These are library API references. The actual docs will be
    available on the index page when they are prepared.

    This class implements all the References REST endpoints. Note that you should always import names from top level.
    eg: ``from polygon import ReferenceClient`` or ``import polygon`` (which allows you to access all names easily)

    Creating the client is as simple as: ``client = ReferenceClient('MY_API_KEY')``
    Once you have the client, you can call its methods to get data from the APIs. All methods have sane default
    values and almost everything can be customized.

    Any method starting with ``async_`` in its name is meant to be for async programming. All methods have their sync
    and async counterparts. Any async method must be awaited while non-async (or sync) methods should be called
    directly.

    Type Hinting tells you what data type a parameter is supposed to be. You should always use ``enums`` for most
    parameters to avoid supplying error prone values.

    It is also a very good idea to visit the `official documentation <https://polygon.io/docs/getting-started>`__. I
    highly recommend using the UI there to play with the endpoints a bit. Observe the
    data you receive as the actual data received through python lib is exactly the same as shown on their page when
    you click ``Run Query``.
    """

    def __init__(self, api_key: str, use_async: bool = False):
        """
        Initiates a Client to be used to access all the endpoints.

        :param api_key: Your API Key. Visit your dashboard to get yours.
        :param use_async: Set to True to get an async client. Defaults to False which returns a non-async client.
        """
        self.KEY, self._async = api_key, use_async
        self.BASE = 'https://api.polygon.io'

        if self._async:
            self.session = httpx.AsyncClient()
        else:
            self.session = requests.session()

        self.session.headers.update({'Authorization': f'Bearer {self.KEY}'})

    # Context Managers
    def __enter__(self):
        if not self._async:
            return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self._async:
            self.session.close()

    # Context Managers - Asyncio
    async def __aenter__(self):
        if self._async:
            return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._async:
            self.session: httpx.AsyncClient
            await self.session.aclose()

    def close(self):
        """
        Closes the ``requests.Session`` and frees up resources. It is recommended to call this method in your
        exit handlers

        Note that this is meant for sync programming only. Use :meth:`async_close` for async.

        :return: None
        """
        if not self._async:
            self.session.close()

    async def async_close(self):
        """
        Closes the ``httpx.AsyncClient`` and frees up resources. It is recommended to call this method in your
        exit handlers. This method should be awaited as this is a coroutine.

        Note that this is meant for async programming only. Use :meth:`close` for sync.

        :return: None
        """
        if self._async:
            self.session: httpx.AsyncClient
            await self.session.aclose()

    # Internal Functions
    def _get_response(self, path: str, params: dict = None,
                      raw_response: bool = True) -> Union[Response, dict]:
        """
        Get response on a path. Meant to be used internally but can be used if you know what you're doing. To be
        used by sync client only. For async access, see :meth:`_get_async_response`

        :param path: RESTful path for the endpoint. Available on the docs for the endpoint right above its name.
        :param params: Query Parameters to be supplied with the request. These are mapped 1:1 with the endpoint.
        :param raw_response: Whether or not to return the ``Response`` Object. Useful for when you need to check the
                             status code or inspect the headers. Defaults to True which returns the ``Response`` object.
        :return: A Response object by default. Make ``raw_response=False`` to get JSON decoded Dictionary
        """
        _res = self.session.request('GET', self.BASE + path, params=params)

        if raw_response:
            return _res

        return _res.json()

    async def _get_async_response(self, path: str, params: dict = None,
                                  raw_response: bool = True) -> Union[HttpxResponse, dict]:
        """
        Get response on a path - meant to be used internally but can be used if you know what you're doing - to be
        used by async client only. For sync access, see :meth:`_get_response`

        :param path: RESTful path for the endpoint. Available on the docs for the endpoint right above its name.
        :param params: Query Parameters to be supplied with the request. These are mapped 1:1 with the endpoint.
        :param raw_response: Whether or not to return the ``Response`` Object. Useful for when you need to check the
                             status code or inspect the headers. Defaults to True which returns the ``Response`` object.
        :return: A Response object by default. Make ``raw_response=False`` to get JSON decoded Dictionary
        """
        _res = await self.session.request('GET', self.BASE + path, params=params)

        if raw_response:
            return _res

        return _res.json()

    def get_next_page_by_url(self, url: str, raw_response: bool = False) -> Union[Response, dict]:
        """
        Get the next page of a response. The URl is returned within ``next_url`` attribute on endpoints which support
        pagination (eg the tickers endpoint). If the response doesn't contain this attribute, either all pages were
        received or the endpoint doesn't have pagination. Meant for internal use primarily.

        Note that this method is meant for sync programming. See :meth:`async_get_next_page_by_url` for async.

        :param url: The next URL. As contained in ``next_url`` of the response.
        :param raw_response: Whether or not to return the ``Response`` Object. Useful for when you need to say check the
                             status code or inspect the headers. Defaults to False which returns the json decoded
                             dictionary.
        :return: Either a Dictionary or a Response object depending on value of raw_response. Defaults to Dict.
        """
        _res = self.session.request('GET', url)

        if raw_response:
            return _res

        return _res.json()

    async def async_get_next_page_by_url(self, url: str, raw_response: bool = False) -> Union[HttpxResponse, dict]:
        """
        Get the next page of a response. The URl is returned within ``next_url`` attribute on endpoints which support
        pagination (eg the tickers endpoint). If the response doesn't contain this attribute, either all pages were
        received or the endpoint doesn't have pagination. Meant for internal use primarily.

        Note that this method is meant for async programming. See :meth:`get_next_page_by_url` for sync.

        :param url: The next URL. As contained in ``next_url`` of the response.
        :param raw_response: Whether or not to return the ``Response`` Object. Useful for when you need to say check the
                             status code or inspect the headers. Defaults to False which returns the json decoded
                             dictionary.
        :return: Either a Dictionary or a Response object depending on value of raw_response. Defaults to Dict.
        """
        _res = await self.session.request('GET', url)

        if raw_response:
            return _res

        return _res.json()

    # Endpoints
    def get_tickers(self, symbol: str = '', ticker_lt=None, ticker_lte=None, ticker_gt=None, ticker_gte=None,
                    symbol_type: str = '', market: str = '', exchange: str = '', cusip: str = None, cik: str = '',
                    date=None, search: str = None,
                    active: bool = True, sort: str = 'ticker', order: str = 'asc', limit: int = 100,
                    raw_response: bool = False) -> Union[Response, dict]:
        """
        Query all ticker symbols which are supported by Polygon.io. This API currently includes Stocks/Equities, Crypto,
        and Forex.
        `Official Docs <https://polygon.io/docs/get_v3_reference_tickers_anchor>`__

        :param symbol: Specify a ticker symbol. Defaults to empty string which queries all tickers.
        :param ticker_lt: Return results where this field is less than the value given
        :param ticker_lte: Return results where this field is less than or equal to the value given
        :param ticker_gt: Return results where this field is greater than the value given
        :param ticker_gte: Return results where this field is greater than or equal to the value given
        :param symbol_type: Specify the type of the tickers. See :class:`polygon.enums.TickerType` for common choices.
                            Find all supported types via the `Ticker Types API
                            <https://polygon.io/docs/get_v2_reference_types_anchor>`__
                            Defaults to empty string which queries all types.
        :param market: Filter by market type. By default all markets are included. See
                       :class:`polygon.enums.TickerMarketType` for available choices.
        :param exchange: Specify the primary exchange of the asset in the ISO code format. Find more information about
                         the ISO codes at the `ISO org website <https://www.iso20022.org/market-identifier-codes>`__.
                         Defaults to empty string which queries all exchanges.
        :param cusip: Specify the ``CUSIP`` code of the asset you want to search for. Find more information about CUSIP
                      codes on `their website <https://www.cusip.com/identifiers.html#/CUSIP>`__
                      Defaults to empty string which queries all CUSIPs
        :param cik: Specify the ``CIK`` of the asset you want to search for. Find more information about CIK codes at
                    `their website <https://www.sec.gov/edgar/searchedgar/cik.htm>`__
                    Defaults to empty string which queries all CIKs.
        :param date: Specify a point in time to retrieve tickers available on that date. Defaults to the most recent
                     available date. Could be ``datetime``, ``date`` or a string ``YYYY-MM-DD``
        :param search: Search for terms within the ticker and/or company name. for eg ``MS`` will match matching symbols
        :param active: Specify if the tickers returned should be actively traded on the queried date. Default is True
        :param sort: The field to sort the results on. Default is ticker. If the search query parameter is present,
                     sort is ignored and results are ordered by relevance. See :class:`polygon.enums.TickerSortType`
                     for available choices.
        :param order: The order to sort the results on. Default is asc. See :class:`polygon.enums.SortOrder` for
                      available choices.
        :param limit: Limit the size of the response, default is 100 and max is 1000. ``Pagination`` is supported by the
                      pagination function below
        :param raw_response: Whether or not to return the ``Response`` Object. Useful for when you need to say check the
                             status code or inspect the headers. Defaults to False which returns the json decoded
                             dictionary.
        :return: A JSON decoded Dictionary by default. Make ``raw_response=True`` to get underlying response object
        """

        if isinstance(date, datetime.date) or isinstance(date, datetime.datetime):
            date = date.strftime('%Y-%m-%d')

        _path = '/v3/reference/tickers'

        _data = {'ticker': symbol, 'ticker.lt': ticker_lt, 'ticker.lte': ticker_lte, 'ticker.gt': ticker_gt,
                 'ticker.gte': ticker_gte, 'type': symbol_type, 'market': market, 'exchange': exchange,
                 'cusip': cusip, 'cik': cik, 'date': date, 'search': search, 'active': active, 'sort': sort,
                 'order': order, 'limit': limit}

        _res = self._get_response(_path, params=_data)

        if raw_response:
            return _res

        return _res.json()

    def get_next_page_tickers(self, old_response: Union[Response, dict],
                              raw_response: bool = False) -> Union[Response, dict, bool]:
        """
        Get the next page using the most recent old response. This function simply parses the next_url attribute
        from the  existing response and uses it to get the next page. Returns False if there is no next page
        remaining (which implies that you have reached the end of all pages).

        :param old_response: The most recent existing response. Can be either ``Response`` Object or Dictionaries
        :param raw_response: Whether or not to return the ``Response`` Object. Useful for when you need to say check the
                             status code or inspect the headers. Defaults to False which returns the json decoded
                             dictionary.
        :return: A JSON decoded Dictionary by default. Make ``raw_response=True`` to get underlying response object
        """

        try:
            if not isinstance(old_response, dict):
                old_response = old_response.json()

            _next_url = old_response['next_url']

            return self.get_next_page_by_url(_next_url, raw_response=raw_response)

        except KeyError:
            return False

    @staticmethod
    def get_ticker_types(*args, **kwargs) -> None:
        """
        DEPRECATED! Replaced by :meth:`get_ticker_types_v3`. This method
        will be removed in a future version from the library.

        Get a mapping of ticker types to their descriptive names.
        `Official Docs <https://polygon.io/docs/get_v2_reference_types_anchor>`__
        """

        print(f'This endpoint has been deprecated and Replaced by New Ticker Types (get_ticker_types_v3). Please Use '
              f'the new endpoint.')
        return

    def get_ticker_types_v3(self, asset_class=None, locale=None, raw_response: bool = False) -> Union[Response, dict]:
        """
        Get a mapping of ticker types to their descriptive names.
        `Official Docs <https://polygon.io/docs/get_v2_reference_types_anchor>`__

        :param asset_class: Filter by asset class. see :class:`polygon.enums.AssetClass` for choices
        :param locale: Filter by locale. See :class:`polygon.enums.Locale` for choices
        :param raw_response: Whether or not to return the ``Response`` Object. Useful for when you need to say check the
                             status code or inspect the headers. Defaults to False which returns the json decoded
                             dictionary.
        :return: A JSON decoded Dictionary by default. Make ``raw_response=True`` to get underlying response object
        """

        _path = '/v3/reference/tickers/types'

        _data = {'asset_class': asset_class,
                 'locale': locale}

        _res = self._get_response(_path, params=_data)

        if raw_response:
            return _res

        return _res.json()

    def get_ticker_details(self, symbol: str, raw_response: bool = False) -> Union[Response, dict]:
        """
        Get details for a ticker symbol's company/entity. This provides a general overview of the entity with
        information such as name, sector, exchange, logo and similar companies.

        This endpoint will be replaced by :meth:`get_ticker_details_vx` in future.
        `Official Docs <https://polygon.io/docs/get_v1_meta_symbols__stocksTicker__company_anchor>`__

        :param symbol: The ticker symbol of the stock/equity.
        :param raw_response: Whether or not to return the ``Response`` Object. Useful for when you need to say check the
                             status code or inspect the headers. Defaults to False which returns the json decoded
                             dictionary.
        :return: A JSON decoded Dictionary by default. Make ``raw_response=True`` to get underlying response object
        """

        _path = f'/v1/meta/symbols/{symbol.upper()}/company'

        _res = self._get_response(_path)

        if raw_response:
            return _res

        return _res.json()

    def get_ticker_details_vx(self, symbol: str, date=None,
                              raw_response: bool = False) -> Union[Response, dict]:
        """
        This API is Experimental and will replace :meth:`get_ticker_details` in future.

        Get a single ticker supported by Polygon.io. This response will have detailed information about the ticker and
        the company behind it.
        `Official Docs <https://polygon.io/docs/get_vX_reference_tickers__ticker__anchor>`__

        :param symbol: The ticker symbol of the asset.
        :param date: Specify a point in time to get information about the ticker available on that date. When retrieving
                     information from SEC filings, we compare this date with the period of report date on the SEC
                     filing. Defaults to the most recent available date.
        :param raw_response: Whether or not to return the ``Response`` Object. Useful for when you need to say check the
                             status code or inspect the headers. Defaults to False which returns the json decoded
                             dictionary.
        :return: A JSON decoded Dictionary by default. Make ``raw_response=True`` to get underlying response object
        """

        if isinstance(date, datetime.date) or isinstance(date, datetime.datetime):
            date = date.strftime('%Y-%m-%d')

        _path = f'/vX/reference/tickers/{symbol.upper()}'

        _data = {'date': date}

        _res = self._get_response(_path, params=_data)

        if raw_response:
            return _res

        return _res.json()

    def get_option_contracts(self, underlying_ticker: str = None, ticker: str = None, contract_type: str = None,
                             expiration_date= None,
                             expiration_date_lt=None, expiration_date_lte=None, expiration_date_gt=None,
                             expiration_date_gte=None, order: str = 'asc', sort: str = None, limit=100,
                             raw_response: bool = False) -> Union[Response, dict]:
        """
        List currently active options contracts
        `Official Docs <https://polygon.io/docs/get_vX_reference_options_contracts_anchor>`__

        :param underlying_ticker: Query for contracts relating to an underlying stock ticker.
        :param ticker: Query for a contract by option ticker.
        :param contract_type: Query by the type of contract. see :class:`polygon.enums.OptionsContractType` for choices
        :param expiration_date: Query by contract expiration date. either ``datetime``, ``date`` or string
                                ``YYYY-MM-DD``
        :param expiration_date_lt: expiration date less than given value
        :param expiration_date_lte: expiration date less than equal to given value
        :param expiration_date_gt: expiration_date greater than given value
        :param expiration_date_gte: expiration_date greater than equal to given value
        :param order: Order of results. See :class:`polygon.enums.SortOrder` for choices.
        :param sort: Sort field for ordering. See :class:`polygon.enums.OptionsContractsSortType` for choices.
        :param limit: Number of results to return
        :param raw_response: Whether or not to return the ``Response`` Object. Useful for when you need to say check the
                             status code or inspect the headers. Defaults to False which returns the json decoded
                             dictionary.
        :return: A JSON decoded Dictionary by default. Make ``raw_response=True`` to get underlying response object
        """
        if isinstance(expiration_date, datetime.date) or isinstance(expiration_date, datetime.datetime):
            expiration_date = expiration_date.strftime('%Y-%m-%d')

        if isinstance(expiration_date_lt, datetime.date) or isinstance(expiration_date_lt, datetime.datetime):
            expiration_date_lt = expiration_date_lt.strftime('%Y-%m-%d')

        if isinstance(expiration_date_lte, datetime.date) or isinstance(expiration_date_lte, datetime.datetime):
            expiration_date_lte = expiration_date_lte.strftime('%Y-%m-%d')

        if isinstance(expiration_date_gt, datetime.date) or isinstance(expiration_date_gt, datetime.datetime):
            expiration_date_gt = expiration_date_gt.strftime('%Y-%m-%d')

        if isinstance(expiration_date_gte, datetime.date) or isinstance(expiration_date_gte, datetime.datetime):
            expiration_date_gte = expiration_date_gte.strftime('%Y-%m-%d')

        _path = f'/vX/reference/options/contracts'

        _data = {'ticker': ticker, 'underlying_ticker': underlying_ticker, 'contract_type': contract_type,
                 'expiration_date': expiration_date, 'expiration_date_lt': expiration_date,
                 'expiration_date_lte': expiration_date_lte, 'expiration_date_gt': expiration_date_gt,
                 'expiration_date_gte': expiration_date_gte, 'order': order, 'sort': sort, 'limit': limit}

        _res = self._get_response(_path, params=_data)

        if raw_response:
            return _res

        return _res.json()

    def get_next_page_option_contracts(self, old_response, raw_response: bool = False) -> Union[Response, dict, bool]:
        """
        Get the next page using the most recent yet old response. This function simply parses the ``next_url``
        attribute from the  existing response and uses it to get the next page. Returns ``False`` if there is no
        next page remaining (which implies that you have reached the end of all pages).

        :param old_response: The most recent existing response. Can be either ``Response`` Object or Dictionaries
        :param raw_response: Whether or not to return the ``Response`` Object. Useful for when you need to say check the
                             status code or inspect the headers. Defaults to False which returns the json decoded
                             dictionary.
        :return: A JSON decoded Dictionary by default. Make ``raw_response=True`` to get underlying response
                 object
        """

        try:
            if not isinstance(old_response, dict):
                old_response = old_response.json()

            _next_url = old_response['next_url']

            return self.get_next_page_by_url(_next_url, raw_response=raw_response)

        except KeyError:
            return False

    def get_ticker_news(self, symbol: str = None, limit: int = 100, order: str = 'desc', sort: str = 'published_utc',
                        ticker_lt=None, ticker_lte=None, ticker_gt=None, ticker_gte=None, published_utc=None,
                        published_utc_lt=None, published_utc_lte=None, published_utc_gt=None, published_utc_gte=None,
                        raw_response: bool = False) -> Union[Response, dict]:
        """
        Get the most recent news articles relating to a stock ticker symbol, including a summary of the article and a
        link to the original source.
        `Official Docs <https://polygon.io/docs/get_v2_reference_news_anchor>`__

        :param symbol: To get news mentioning the name given. Defaults to empty string which doesn't filter tickers
        :param limit: Limit the size of the response, default is 100 and max is 1000. Use pagination helper function
                      for larger responses.
        :param order: Order the results. See :class:`polygon.enums.SortOrder` for choices.
        :param sort: The field key to sort. See :class:`polygon.enums.TickerNewsSort` for choices.
        :param ticker_lt: Return results where this field is less than the value.
        :param ticker_lte: Return results where this field is less than or equal to the value.
        :param ticker_gt: Return results where this field is greater than the value
        :param ticker_gte: Return results where this field is greater than or equal to the value.
        :param published_utc: A date string ``YYYY-MM-DD`` or ``datetime`` for published date time filters.
        :param published_utc_lt: Return results where this field is less than the value given
        :param published_utc_lte: Return results where this field is less than or equal to the value given
        :param published_utc_gt: Return results where this field is greater than the value given
        :param published_utc_gte: Return results where this field is greater than or equal to the value given
        :param raw_response: Whether or not to return the ``Response`` Object. Useful for when you need to say check the
                             status code or inspect the headers. Defaults to False which returns the json decoded
                             dictionary.
        :return: A JSON decoded Dictionary by default. Make ``raw_response=True`` to get underlying response object
        """

        if isinstance(published_utc, datetime.date) or isinstance(published_utc, datetime.datetime):
            published_utc = published_utc.strftime('%Y-%m-%d')

        if isinstance(published_utc_lt, datetime.date) or isinstance(published_utc_lt, datetime.datetime):
            published_utc_lt = published_utc_lt.strftime('%Y-%m-%d')

        if isinstance(published_utc_lte, datetime.date) or isinstance(published_utc_lte, datetime.datetime):
            published_utc_lte = published_utc_lte.strftime('%Y-%m-%d')

        if isinstance(published_utc_gt, datetime.date) or isinstance(published_utc_gt, datetime.datetime):
            published_utc_gt = published_utc_gt.strftime('%Y-%m-%d')

        if isinstance(published_utc_gte, datetime.date) or isinstance(published_utc_gte, datetime.datetime):
            published_utc_gte = published_utc_gte.strftime('%Y-%m-%d')

        _path = '/v2/reference/news'

        _data = {'limit': limit, 'order': order, 'sort': sort, 'ticker': symbol, 'ticker.lt': ticker_lt,
                 'ticker.lte': ticker_lte, 'ticker.gt': ticker_gt, 'ticker.gte': ticker_gte,
                 'published_utc': published_utc, 'published_utc.lt': published_utc_lt,
                 'published_utc.lte': published_utc_lte, 'published_utc.gt': published_utc_gt,
                 'published_utc.gte': published_utc_gte}

        _res = self._get_response(_path, params=_data)

        if raw_response:
            return _res

        return _res.json()

    def get_next_page_news(self, old_response: Union[Response, dict],
                           raw_response: bool = False) -> Union[Response, dict, bool]:
        """
        Get the next page using the most recent yet old response. This function simply parses the ``next_url`` attribute
        from the existing response and uses it to get the next page. Returns ``False`` if there is no next page
        remaining (which implies that you have reached the end of all pages).

        :param old_response: The most recent existing response. Can be either ``Response`` Object or Dictionaries
        :param raw_response: Whether or not to return the ``Response`` Object. Useful for when you need to say check the
                             status code or inspect the headers. Defaults to False which returns the json decoded
                             dictionary.
        :return: A JSON decoded Dictionary by default. Make ``raw_response=True`` to get underlying response object
        """

        try:
            if not isinstance(old_response, dict):
                old_response = old_response.json()

            _next_url = old_response['next_url']

            return self.get_next_page_by_url(_next_url, raw_response=raw_response)

        except KeyError:
            return False

    def get_stock_dividends(self, symbol: str, raw_response: bool = False) -> Union[Response, dict]:
        """
        Get a list of historical dividends for a stock, including the relevant dates and the amount of the dividend.
        `Official Docs <https://polygon.io/docs/get_v2_reference_dividends__stocksTicker__anchor>`__

        :param symbol: The ticker symbol of the stock/equity.
        :param raw_response: Whether or not to return the ``Response`` Object. Useful for when you need to say check the
                             status code or inspect the headers. Defaults to False which returns the json decoded
                             dictionary.
        :return: A JSON decoded Dictionary by default. Make ``raw_response=True`` to get underlying response object
        """

        _path = f'/v2/reference/dividends/{symbol.upper()}'

        _res = self._get_response(_path)

        if raw_response:
            return _res

        return _res.json()

    def get_stock_financials(self, symbol: str, limit: int = 100, report_type: str = None, sort: str = None,
                             raw_response: bool = False) -> Union[Response, dict]:
        """
        Get historical financial data for a stock ticker. This API will be replaced by
        :meth:`get_stock_financials_vx` in future.
        `Official Docs <https://polygon.io/docs/get_v2_reference_financials__stocksTicker__anchor>`__

        :param symbol: The ticker symbol of the stock/equity.
        :param limit: Limit the number of results. Defaults to 100
        :param report_type: Specify a type of report to return. see :class:`polygon.enums.StockReportType` for
                            choices. Defaults to ``None``
        :param sort: The key for sorting the results. see :class:`polygon.enums.StockFinancialsSortType` for choices.
        :param raw_response: Whether or not to return the ``Response`` Object. Useful for when you need to say check the
                             status code or inspect the headers. Defaults to False which returns the json decoded
                             dictionary.
        :return: A JSON decoded Dictionary by default. Make ``raw_response=True`` to get underlying response object
        """

        _path = f'/v2/reference/financials/{symbol.upper()}'

        _data = {'limit': limit,
                 'type': report_type,
                 'sort': sort}

        _res = self._get_response(_path, params=_data)

        if raw_response:
            return _res

        return _res.json()

    def get_stock_financials_vx(self, ticker: str = None, cik: str = None, company_name: str = None,
                                company_name_search: str = None, sic: str = None, filing_date=None,
                                filing_date_lt=None, filing_date_lte=None, filing_date_gt=None, filing_date_gte=None,
                                period_of_report_date=None, period_of_report_date_lt=None,
                                period_of_report_date_lte=None, period_of_report_date_gt=None,
                                period_of_report_date_gte=None, time_frame=None, include_sources: bool = False,
                                order: str = 'asc', limit: int = 50, sort: str = 'filing_date',
                                raw_response: bool = False):
        """
        Get historical financial data for a stock ticker. The financials data is extracted from XBRL from company SEC
        filings using `this methodology <http://xbrl.squarespace.com/understanding-sec-xbrl-financi/>`__
        `Official Docs <https://polygon.io/docs/get_vX_reference_financials_anchor>`__

        This API is experimental and will replace :meth:`get_stock_financials` in future.

        :param ticker: Filter query by company ticker.
        :param cik: filter the Query by ``central index key (CIK)`` Number
        :param company_name: filter the query by company name
        :param company_name_search: partial match text search for company names
        :param sic: Query by ``standard industrial classification (SIC)``
        :param filing_date: Query by the date when the filing with financials data was filed. ``datetime/date`` or
                            string ``YYYY-MM-DD``
        :param filing_date_lt: filter for filing date less than given value
        :param filing_date_lte: filter for filing date less than equal to given value
        :param filing_date_gt: filter for filing date greater than given value
        :param filing_date_gte: filter for filing date greater than equal to given value
        :param period_of_report_date: query by The period of report for the filing with financials data.
                                      ``datetime/date`` or string in format: ``YYY-MM-DD``.
        :param period_of_report_date_lt: filter for period of report date less than given value
        :param period_of_report_date_lte: filter for period of report date less than equal to given value
        :param period_of_report_date_gt: filter for period of report date greater than given value
        :param period_of_report_date_gte: filter for period of report date greater than equal to given value
        :param time_frame: Query by timeframe. Annual financials originate from 10-K filings, and quarterly financials
                           originate from 10-Q filings. Note: Most companies do not file quarterly reports for Q4 and
                           instead include those financials in their annual report, so some companies my not return
                           quarterly financials for Q4. See :class:`polygon.enums.StockFinancialsTimeframe` for choices.
        :param include_sources: Whether or not to include the xpath and formula attributes for each financial data
                                point. See the xpath and formula response attributes for more info. ``False`` by default
        :param order: Order results based on the sort field. 'asc' by default. See :class:`polygon.enums.SortOrder`
                      for choices.
        :param limit: number of max results to obtain. defaults to 50.
        :param sort: Sort field key used for ordering. 'filing_date' default. see
                     :class:`polygon.enums.StockFinancialsSortKey` for choices.
        :param raw_response: Whether or not to return the ``Response`` Object. Useful for when you need to say check the
                             status code or inspect the headers. Defaults to False which returns the json decoded
                             dictionary.
        :return: A JSON decoded Dictionary by default. Make ``raw_response=True`` to get underlying response object
        """

        _path = f'/vX/reference/financials'

        _data = {'ticker': ticker, 'cik': cik, 'company_name': company_name,
                 'company_name_search': company_name_search, 'sic': sic, 'filing_date': filing_date,
                 'filing_date_lt': filing_date_lt, 'filing_date_lte': filing_date_lte,
                 'filing_date_gt': filing_date_gt, 'filing_date_gte': filing_date_gte,
                 'period_of_report_date': period_of_report_date, 'period_of_report_date_lt': period_of_report_date_lt,
                 'period_of_report_date_lte': period_of_report_date_lte,
                 'period_of_report_date_gt': period_of_report_date_gt,
                 'period_of_report_date_gte': period_of_report_date_gte, 'timeframe': time_frame, 'order': order,
                 'include_sources': 'true' if include_sources else 'false', 'limit': limit, 'sort': sort}

        _res = self._get_response(_path, params=_data)

        if raw_response:
            return _res

        return _res.json()

    def get_stock_splits(self, symbol: str, raw_response: bool = False) -> Union[Response, dict]:
        """
        Get a list of historical stock splits for a ticker symbol, including the execution and payment dates of the
        stock split, and the split ratio.
        `Official Docs <https://polygon.io/docs/get_v2_reference_splits__stocksTicker__anchor>`__

        :param symbol: The ticker symbol of the stock/equity.
        :param raw_response: Whether or not to return the ``Response`` Object. Useful for when you need to say check the
                             status code or inspect the headers. Defaults to False which returns the json decoded
                             dictionary.
        :return: A JSON decoded Dictionary by default. Make ``raw_response=True`` to get underlying response object
        """

        _path = f'/v2/reference/splits/{symbol.upper()}'

        _res = self._get_response(_path)

        if raw_response:
            return _res

        return _res.json()

    def get_market_holidays(self, raw_response: bool = False) -> Union[Response, dict]:
        """
        Get upcoming market holidays and their open/close times.
        `Official Docs <https://polygon.io/docs/get_v1_marketstatus_upcoming_anchor>`__

        :param raw_response: Whether or not to return the ``Response`` Object. Useful for when you need to say check the
                             status code or inspect the headers. Defaults to False which returns the json decoded
                             dictionary.
        :return: A JSON decoded Dictionary by default. Make ``raw_response=True`` to get underlying response object
        """

        _path = '/v1/marketstatus/upcoming'

        _res = self._get_response(_path)

        if raw_response:
            return _res

        return _res.json()

    def get_market_status(self, raw_response: bool = False) -> Union[Response, dict]:
        """
        Get the current trading status of the exchanges and overall financial markets.
        `Official Docs <https://polygon.io/docs/get_v1_marketstatus_now_anchor>`__

        :param raw_response: Whether or not to return the ``Response`` Object. Useful for when you need to say check the
                             status code or inspect the headers. Defaults to False which returns the json decoded
                             dictionary.
        :return: A JSON decoded Dictionary by default. Make ``raw_response=True`` to get underlying response object
        """

        _path = '/v1/marketstatus/now'

        _res = self._get_response(_path)

        if raw_response:
            return _res

        return _res.json()

    def get_condition_mappings(self, tick_type: str = 'trades', raw_response: bool = False) -> Union[Response, dict]:
        """
        Get a unified numerical mapping for conditions on trades and quotes. Each feed/exchange uses its own set of
        codes to identify conditions, so the same condition may have a different code depending on the originator of
        the data. Polygon.io defines its own mapping to allow for uniformly identifying a condition across
        feeds/exchanges.
        `Official Docs <https://polygon.io/docs/get_v1_meta_conditions__ticktype__anchor>`__

        :param tick_type: The type of ticks to return mappings for. Defaults to 'trades'. See
                          :class:`polygon.enums.ConditionMappingTickType` for choices.
        :param raw_response: Whether or not to return the ``Response`` Object. Useful for when you need to say check the
                             status code or inspect the headers. Defaults to False which returns the json decoded
                             dictionary.
        :return: A JSON decoded Dictionary by default. Make ``raw_response=True`` to get underlying response object
        """

        _path = f'/v1/meta/conditions/{tick_type.lower()}'

        _res = self._get_response(_path)

        if raw_response:
            return _res

        return _res.json()

    def get_conditions(self, asset_class: str = None, data_type: str = None, id=None, sip=None, order=None,
                       limit: int = 50, sort: str = 'name', raw_response: bool = False):
        """
        List all conditions that Polygon.io uses.
        `Official Docs <https://polygon.io/docs/get_v1_meta_conditions__ticktype__anchor>`__

        :param asset_class: Filter for conditions within a given asset class. See :class:`polygon.enums.AssetClass`
                            for choices. Defaults to all assets.
        :param data_type: Filter by data type. See :class:`polygon.enums.ConditionsDataType` for choices. defaults to
                          all.
        :param id: Filter for conditions with a given ID
        :param sip: Filter by SIP. If the condition contains a mapping for that SIP, the condition will be returned.
        :param order: Order results. See :class:`polygon.enums.SortOrder` for choices.
        :param limit: limit the number of results. defaults to 50.
        :param sort: Sort field used for ordering. Defaults to 'name'. See :class:`polygon.enums.ConditionsSortKey`
                     for choices.
        :param raw_response: Whether or not to return the ``Response`` Object. Useful for when you need to say check the
                             status code or inspect the headers. Defaults to False which returns the json decoded
                             dictionary.
        :return: A JSON decoded Dictionary by default. Make ``raw_response=True`` to get underlying response object
        """
        _path = f'/vX/reference/conditions'

        _data = {'asset_class': asset_class, 'data_type': data_type, 'id': id, 'sip': sip, 'order': order,
                 'limit': limit, 'sort': sort}

        _res = self._get_response(_path, params=_data)

        if raw_response:
            return _res

        return _res.json()

    def get_exchanges(self, asset_class: str = None, locale: str = None, raw_response: bool = False):
        """
        List all exchanges that Polygon.io knows about.
        `Official Docs <https://polygon.io/docs/get_v3_reference_exchanges_anchor>`__

        :param asset_class: filter by asset class. See :class:`polygon.enums.AssetClass` for choices.
        :param locale: Filter by locale name. See :class:`polygon.enums.Locale`
        :param raw_response: Whether or not to return the ``Response`` Object. Useful for when you need to say check the
                             status code or inspect the headers. Defaults to False which returns the json decoded
                             dictionary.
        :return: A JSON decoded Dictionary by default. Make ``raw_response=True`` to get underlying response object
        """

        _path = f'/v3/reference/exchanges'

        _data = {'asset_class': asset_class, 'locale': locale}

        _res = self._get_response(_path, params=_data)

        if raw_response:
            return _res

        return _res.json()

    @staticmethod
    def get_stock_exchanges(*args, **kwargs):
        """
        DEPRECATED! Replaced by :meth:`get_exchanges`. This method will be removed in a future version from the library

        """
        print(f'This endpoint has been deprecated and replaced by new Exchanges endpoint. Please use get_exchanges().')
        return

    @staticmethod
    def get_crypto_exchanges(*args, **kwargs):
        """
        DEPRECATED! Replaced by :meth:`get_exchanges`. This method
        will be removed in a future version from the library

        """
        print(f'This endpoint has been deprecated and replaced by new Exchanges endpoint. Please use get_exchanges().')
        return

    def get_locales(self, raw_response: bool = False) -> Union[Response, dict]:
        """
        Get a list of locales currently supported by Polygon.io.
        `Official Docs <https://polygon.io/docs/get_v2_reference_locales_anchor>`__

        :param raw_response: Whether or not to return the ``Response`` Object. Useful for when you need to say check the
                             status code or inspect the headers. Defaults to False which returns the json decoded
                             dictionary.
        :return: A JSON decoded Dictionary by default. Make ``raw_response=True`` to get underlying response object
        """

        _path = '/v2/reference/locales'

        _res = self._get_response(_path)

        if raw_response:
            return _res

        return _res.json()

    def get_markets(self, raw_response: bool = False) -> Union[Response, dict]:
        """
        Get a list of markets that are currently supported by Polygon.io.
        `Official Docs <https://polygon.io/docs/get_v2_reference_markets_anchor>`__

        :param raw_response: Whether or not to return the ``Response`` Object. Useful for when you need to say check the
                             status code or inspect the headers. Defaults to False which returns the json decoded
                             dictionary.
        :return: A JSON decoded Dictionary by default. Make ``raw_response=True`` to get underlying response object
        """

        _path = '/v2/reference/markets'

        _res = self._get_response(_path)

        if raw_response:
            return _res

        return _res.json()

    # ASYNC Operations' Methods
    async def async_get_tickers(self, symbol: str = '', ticker_lt=None, ticker_lte=None, ticker_gt=None,
                                ticker_gte=None, symbol_type: str = '', market: str = '', exchange: str = '',
                                cusip: str = None, cik: str = '', date: Union[str, datetime.date, datetime.datetime]
                                = None, search: str = None, active: bool = True, sort: str = 'ticker', order: str =
                                'asc', limit: int = 100, raw_response: bool = False) -> Union[HttpxResponse, dict]:
        """
        Query all ticker symbols which are supported by Polygon.io. This API currently includes Stocks/Equities, Crypto,
        and Forex - Assync method
        `Official Docs <https://polygon.io/docs/get_v3_reference_tickers_anchor>`__

        :param symbol: Specify a ticker symbol. Defaults to empty string which queries all tickers.
        :param ticker_lt: Return results where this field is less than the value given
        :param ticker_lte: Return results where this field is less than or equal to the value given
        :param ticker_gt: Return results where this field is greater than the value given
        :param ticker_gte: Return results where this field is greater than or equal to the value given
        :param symbol_type: Specify the type of the tickers. See :class:`polygon.enums.TickerType` for common choices.
                            Find all supported types via the `Ticker Types API
                            <https://polygon.io/docs/get_v2_reference_types_anchor>`__
                            Defaults to empty string which queries all types.
        :param market: Filter by market type. By default all markets are included. See
                       :class:`polygon.enums.TickerMarketType` for available choices.
        :param exchange: Specify the primary exchange of the asset in the ISO code format. Find more information about
                         the ISO codes at the `ISO org website <https://www.iso20022.org/market-identifier-codes>`__.
                         Defaults to empty string which queries all exchanges.
        :param cusip: Specify the ``CUSIP`` code of the asset you want to search for. Find more information about CUSIP
                      codes on `their website <https://www.cusip.com/identifiers.html#/CUSIP>`__
                      Defaults to empty string which queries all CUSIPs
        :param cik: Specify the ``CIK`` of the asset you want to search for. Find more information about CIK codes at
                    `their website <https://www.sec.gov/edgar/searchedgar/cik.htm>`__
                    Defaults to empty string which queries all CIKs.
        :param date: Specify a point in time to retrieve tickers available on that date. Defaults to the most recent
                     available date. Could be ``datetime``, ``date`` or a string ``YYYY-MM-DD``
        :param search: Search for terms within the ticker and/or company name. for eg ``MS`` will match matching symbols
        :param active: Specify if the tickers returned should be actively traded on the queried date. Default is True
        :param sort: The field to sort the results on. Default is ticker. If the search query parameter is present,
                     sort is ignored and results are ordered by relevance. See :class:`polygon.enums.TickerSortType`
                     for available choices.
        :param order: The order to sort the results on. Default is asc. See :class:`polygon.enums.SortOrder` for
                      available choices.
        :param limit: Limit the size of the response, default is 100 and max is 1000. ``Pagination`` is supported by the
                      pagination function below
        :param raw_response: Whether or not to return the ``Response`` Object. Useful for when you need to say check the
                             status code or inspect the headers. Defaults to False which returns the json decoded
                             dictionary.
        :return: A JSON decoded Dictionary by default. Make ``raw_response=True`` to get underlying response object
        """

        if isinstance(date, datetime.date) or isinstance(date, datetime.datetime):
            date = date.strftime('%Y-%m-%d')

        _path = '/v3/reference/tickers'

        _data = {'ticker': symbol, 'ticker.lt': ticker_lt, 'ticker.lte': ticker_lte, 'ticker.gt': ticker_gt,
                 'ticker.gte': ticker_gte, 'type': symbol_type, 'market': market, 'exchange': exchange,
                 'cusip': cusip, 'cik': cik, 'date': date, 'search': search, 'active': active, 'sort': sort,
                 'order': order, 'limit': limit}

        _res = await self._get_async_response(_path, params=_data)

        if raw_response:
            return _res

        return _res.json()

    async def async_get_next_page_tickers(self, old_response: Union[HttpxResponse, dict],
                                          raw_response: bool = False) -> Union[HttpxResponse, dict, bool]:
        """
        Get the next page using the most recent old response. This function simply parses the next_url attribute
        from the  existing response and uses it to get the next page. Returns False if there is no next page
        remaining (which implies that you have reached the end of all pages) - Async method

        :param old_response: The most recent existing response. Can be either ``Response`` Object or Dictionaries
        :param raw_response: Whether or not to return the ``Response`` Object. Useful for when you need to say check the
                             status code or inspect the headers. Defaults to False which returns the json decoded
                             dictionary.
        :return: A JSON decoded Dictionary by default. Make ``raw_response=True`` to get underlying response object
        """

        try:
            if not isinstance(old_response, dict):
                old_response = old_response.json()

            _next_url = old_response['next_url']

            return await self.async_get_next_page_by_url(_next_url, raw_response=raw_response)

        except KeyError:
            return False

    @staticmethod
    async def async_get_ticker_types(*args, **kwargs) -> None:
        """
        DEPRECATED! Replaced by :meth:`async_get_ticker_types_v3`. This method
        will be removed in a future version from the library.

        Get a mapping of ticker types to their descriptive names.
        `Official Docs <https://polygon.io/docs/get_v2_reference_types_anchor>`__

        """

        print(f'This endpoint has been deprecated and Replaced by New Ticker Types (async_get_ticker_types_v3). Please '
              f'Use  the new endpoint.')
        return

    async def async_get_ticker_types_v3(self, asset_class=None, locale=None,
                                        raw_response: bool = False) -> Union[HttpxResponse, dict]:
        """
        Get a mapping of ticker types to their descriptive names - Async method
        `Official Docs <https://polygon.io/docs/get_v2_reference_types_anchor>`__

        :param asset_class: Filter by asset class. see :class:`polygon.enums.AssetClass` for choices
        :param locale: Filter by locale. See :class:`polygon.enums.Locale` for choices
        :param raw_response: Whether or not to return the ``Response`` Object. Useful for when you need to say check the
                             status code or inspect the headers. Defaults to False which returns the json decoded
                             dictionary.
        :return: A JSON decoded Dictionary by default. Make ``raw_response=True`` to get underlying response object
        """

        _path = '/v3/reference/tickers/types'

        _data = {'asset_class': asset_class,
                 'locale': locale}

        _res = await self._get_async_response(_path, params=_data)

        if raw_response:
            return _res

        return _res.json()

    async def async_get_ticker_details(self, symbol: str, raw_response: bool = False) -> Union[HttpxResponse, dict]:
        """
        Get details for a ticker symbol's company/entity. This provides a general overview of the entity with
        information such as name, sector, exchange, logo and similar companies - Async method

        This endpoint will be replaced by :meth:`async_get_ticker_details_vx` in future.
        `Official Docs <https://polygon.io/docs/get_v1_meta_symbols__stocksTicker__company_anchor>`__

        :param symbol: The ticker symbol of the stock/equity.
        :param raw_response: Whether or not to return the ``Response`` Object. Useful for when you need to say check the
                             status code or inspect the headers. Defaults to False which returns the json decoded
                             dictionary.
        :return: A JSON decoded Dictionary by default. Make ``raw_response=True`` to get underlying response object
        """

        _path = f'/v1/meta/symbols/{symbol.upper()}/company'

        _res = await self._get_async_response(_path)

        if raw_response:
            return _res

        return _res.json()

    async def async_get_ticker_details_vx(self, symbol: str, date=None,
                                          raw_response: bool = False) -> Union[HttpxResponse, dict]:
        """
        This API is Experimental and will replace :meth:`async_get_ticker_details` in future - Async method

        Get a single ticker supported by Polygon.io. This response will have detailed information about the ticker and
        the company behind it.
        `Official Docs <https://polygon.io/docs/get_vX_reference_tickers__ticker__anchor>`__

        :param symbol: The ticker symbol of the asset.
        :param date: Specify a point in time to get information about the ticker available on that date. When retrieving
                     information from SEC filings, we compare this date with the period of report date on the SEC
                     filing. Defaults to the most recent available date.
        :param raw_response: Whether or not to return the ``Response`` Object. Useful for when you need to say check the
                             status code or inspect the headers. Defaults to False which returns the json decoded
                             dictionary.
        :return: A JSON decoded Dictionary by default. Make ``raw_response=True`` to get underlying response object
        """

        if isinstance(date, datetime.date) or isinstance(date, datetime.datetime):
            date = date.strftime('%Y-%m-%d')

        _path = f'/vX/reference/tickers/{symbol.upper()}'

        _data = {'date': date}

        _res = await self._get_async_response(_path, params=_data)

        if raw_response:
            return _res

        return _res.json()

    async def async_get_option_contracts(self, underlying_ticker: str = None, ticker: str = None,
                                         contract_type: str = None,
                                         expiration_date= None,
                                         expiration_date_lt=None, expiration_date_lte=None, expiration_date_gt=None,
                                         expiration_date_gte=None, order: str = 'asc', sort: str = None,
                                         limit: int = 50,
                                         raw_response: bool = False) -> Union[HttpxResponse, dict]:
        """
        List currently active options contracts - Async method
        `Official Docs <https://polygon.io/docs/get_vX_reference_options_contracts_anchor>`__

        :param underlying_ticker: Query for contracts relating to an underlying stock ticker.
        :param ticker: Query for a contract by option ticker.
        :param contract_type: Query by the type of contract. see :class:`polygon.enums.OptionsContractType` for choices
        :param expiration_date: Query by contract expiration date. either ``datetime``, ``date`` or string
                                ``YYYY-MM-DD``
        :param expiration_date_lt: expiration date less than given value
        :param expiration_date_lte: expiration date less than equal to given value
        :param expiration_date_gt: expiration_date greater than given value
        :param expiration_date_gte: expiration_date greater than equal to given value
        :param order: Order of results. See :class:`polygon.enums.SortOrder` for choices.
        :param sort: Sort field for ordering. See :class:`polygon.enums.OptionsContractsSortType` for choices.
        :param limit: Number of results to return
        :param raw_response: Whether or not to return the ``Response`` Object. Useful for when you need to say check the
                             status code or inspect the headers. Defaults to False which returns the json decoded
                             dictionary.
        :return: A JSON decoded Dictionary by default. Make ``raw_response=True`` to get underlying response object
        """
        if isinstance(expiration_date, datetime.date) or isinstance(expiration_date, datetime.datetime):
            expiration_date = expiration_date.strftime('%Y-%m-%d')

        if isinstance(expiration_date_lt, datetime.date) or isinstance(expiration_date_lt, datetime.datetime):
            expiration_date_lt = expiration_date_lt.strftime('%Y-%m-%d')

        if isinstance(expiration_date_lte, datetime.date) or isinstance(expiration_date_lte, datetime.datetime):
            expiration_date_lte = expiration_date_lte.strftime('%Y-%m-%d')

        if isinstance(expiration_date_gt, datetime.date) or isinstance(expiration_date_gt, datetime.datetime):
            expiration_date_gt = expiration_date_gt.strftime('%Y-%m-%d')

        if isinstance(expiration_date_gte, datetime.date) or isinstance(expiration_date_gte, datetime.datetime):
            expiration_date_gte = expiration_date_gte.strftime('%Y-%m-%d')

        _path = f'/vX/reference/options/contracts'

        _data = {'ticker': ticker, 'underlying_ticker': underlying_ticker, 'contract_type': contract_type,
                 'expiration_date': expiration_date, 'expiration_date_lt': expiration_date,
                 'expiration_date_lte': expiration_date_lte, 'expiration_date_gt': expiration_date_gt,
                 'expiration_date_gte': expiration_date_gte, 'order': order, 'sort': sort, 'limit': limit}

        _res = await self._get_async_response(_path, params=_data)

        if raw_response:
            return _res

        return _res.json()

    async def async_get_ticker_news(self, symbol: str = None, limit: int = 100, order: str = 'desc',
                                    sort: str = 'published_utc',
                                    ticker_lt=None, ticker_lte=None, ticker_gt=None, ticker_gte=None,
                                    published_utc=None, published_utc_lt=None, published_utc_lte=None,
                                    published_utc_gt=None, published_utc_gte=None,
                                    raw_response: bool = False) -> Union[HttpxResponse, dict]:
        """
        Get the most recent news articles relating to a stock ticker symbol, including a summary of the article and a
        link to the original source - Async method
        `Official Docs <https://polygon.io/docs/get_v2_reference_news_anchor>`__

        :param symbol: To get news mentioning the name given. Defaults to empty string which doesn't filter tickers
        :param limit: Limit the size of the response, default is 100 and max is 1000. Use pagination helper function
                      for larger responses.
        :param order: Order the results. See :class:`polygon.enums.SortOrder` for choices.
        :param sort: The field key to sort. See :class:`polygon.enums.TickerNewsSort` for choices.
        :param ticker_lt: Return results where this field is less than the value.
        :param ticker_lte: Return results where this field is less than or equal to the value.
        :param ticker_gt: Return results where this field is greater than the value
        :param ticker_gte: Return results where this field is greater than or equal to the value.
        :param published_utc: A date string ``YYYY-MM-DD`` or ``datetime`` for published date time filters.
        :param published_utc_lt: Return results where this field is less than the value given
        :param published_utc_lte: Return results where this field is less than or equal to the value given
        :param published_utc_gt: Return results where this field is greater than the value given
        :param published_utc_gte: Return results where this field is greater than or equal to the value given
        :param raw_response: Whether or not to return the ``Response`` Object. Useful for when you need to say check the
                             status code or inspect the headers. Defaults to False which returns the json decoded
                             dictionary.
        :return: A JSON decoded Dictionary by default. Make ``raw_response=True`` to get underlying response object
        """

        if isinstance(published_utc, datetime.date) or isinstance(published_utc, datetime.datetime):
            published_utc = published_utc.strftime('%Y-%m-%d')

        if isinstance(published_utc_lt, datetime.date) or isinstance(published_utc_lt, datetime.datetime):
            published_utc_lt = published_utc_lt.strftime('%Y-%m-%d')

        if isinstance(published_utc_lte, datetime.date) or isinstance(published_utc_lte, datetime.datetime):
            published_utc_lte = published_utc_lte.strftime('%Y-%m-%d')

        if isinstance(published_utc_gt, datetime.date) or isinstance(published_utc_gt, datetime.datetime):
            published_utc_gt = published_utc_gt.strftime('%Y-%m-%d')

        if isinstance(published_utc_gte, datetime.date) or isinstance(published_utc_gte, datetime.datetime):
            published_utc_gte = published_utc_gte.strftime('%Y-%m-%d')

        _path = '/v2/reference/news'

        _data = {'limit': limit, 'order': order, 'sort': sort, 'ticker': symbol, 'ticker.lt': ticker_lt,
                 'ticker.lte': ticker_lte, 'ticker.gt': ticker_gt, 'ticker.gte': ticker_gte,
                 'published_utc': published_utc, 'published_utc.lt': published_utc_lt,
                 'published_utc.lte': published_utc_lte, 'published_utc.gt': published_utc_gt,
                 'published_utc.gte': published_utc_gte}

        _res = await self._get_async_response(_path, params=_data)

        if raw_response:
            return _res

        return _res.json()

    async def async_get_next_page_news(self, old_response: Union[HttpxResponse, dict],
                                       raw_response: bool = False) -> Union[HttpxResponse, dict, bool]:
        """
        Get the next page using the most recent yet old response. This function simply parses the ``next_url`` attribute
        from the existing response and uses it to get the next page. Returns ``False`` if there is no next page
        remaining (which implies that you have reached the end of all pages) - Async method

        :param old_response: The most recent existing response. Can be either ``Response`` Object or Dictionaries
        :param raw_response: Whether or not to return the ``Response`` Object. Useful for when you need to say check the
                             status code or inspect the headers. Defaults to False which returns the json decoded
                             dictionary.
        :return: A JSON decoded Dictionary by default. Make ``raw_response=True`` to get underlying response object
        """

        try:
            if not isinstance(old_response, dict):
                old_response = old_response.json()

            _next_url = old_response['next_url']

            return await self.async_get_next_page_by_url(_next_url, raw_response=raw_response)

        except KeyError:
            return False

    async def async_get_stock_dividends(self, symbol: str, raw_response: bool = False) -> Union[HttpxResponse, dict]:
        """
        Get a list of historical dividends for a stock, including the relevant dates and the amount of the dividend -
        Async method
        `Official Docs <https://polygon.io/docs/get_v2_reference_dividends__stocksTicker__anchor>`__

        :param symbol: The ticker symbol of the stock/equity.
        :param raw_response: Whether or not to return the ``Response`` Object. Useful for when you need to say check the
                             status code or inspect the headers. Defaults to False which returns the json decoded
                             dictionary.
        :return: A JSON decoded Dictionary by default. Make ``raw_response=True`` to get underlying response object
        """

        _path = f'/v2/reference/dividends/{symbol.upper()}'

        _res = await self._get_async_response(_path)

        if raw_response:
            return _res

        return _res.json()

    async def async_get_stock_financials(self, symbol: str, limit: int = 100, report_type: str = None, sort: str = None,
                                         raw_response: bool = False) -> Union[HttpxResponse, dict]:
        """
        Get historical financial data for a stock ticker. This API will be replaced by
        :meth:`async_get_stock_financials_vx` in future - Async method
        `Official Docs <https://polygon.io/docs/get_v2_reference_financials__stocksTicker__anchor>`__

        :param symbol: The ticker symbol of the stock/equity.
        :param limit: Limit the number of results. Defaults to 100
        :param report_type: Specify a type of report to return. see :class:`polygon.enums.StockReportType` for
                            choices. Defaults to ``None``
        :param sort: The key for sorting the results. see :class:`polygon.enums.StockFinancialsSortType` for choices.
        :param raw_response: Whether or not to return the ``Response`` Object. Useful for when you need to say check the
                             status code or inspect the headers. Defaults to False which returns the json decoded
                             dictionary.
        :return: A JSON decoded Dictionary by default. Make ``raw_response=True`` to get underlying response object
        """

        _path = f'/v2/reference/financials/{symbol.upper()}'

        _data = {'limit': limit,
                 'type': report_type,
                 'sort': sort}

        _res = await self._get_async_response(_path, params=_data)

        if raw_response:
            return _res

        return _res.json()

    async def async_get_stock_financials_vx(self, ticker: str = None, cik: str = None, company_name: str = None,
                                            company_name_search: str = None, sic: str = None, filing_date=None,
                                            filing_date_lt=None, filing_date_lte=None, filing_date_gt=None,
                                            filing_date_gte=None, period_of_report_date=None,
                                            period_of_report_date_lt=None, period_of_report_date_lte=None,
                                            period_of_report_date_gt=None, period_of_report_date_gte=None,
                                            time_frame=None, include_sources: bool = False, order: str = 'asc',
                                            limit: int = 50, sort: str = 'filing_date', raw_response: bool = False):
        """
        Get historical financial data for a stock ticker. The financials data is extracted from XBRL from company SEC
        filings using `this methodology <http://xbrl.squarespace.com/understanding-sec-xbrl-financi/>`__ - Async method
        `Official Docs <https://polygon.io/docs/get_vX_reference_financials_anchor>`__

        This API is experimental and will replace :meth:`async_get_stock_financials` in future.

        :param ticker: Filter query by company ticker.
        :param cik: filter the Query by ``central index key (CIK)`` Number
        :param company_name: filter the query by company name
        :param company_name_search: partial match text search for company names
        :param sic: Query by ``standard industrial classification (SIC)``
        :param filing_date: Query by the date when the filing with financials data was filed. ``datetime/date`` or
                            string ``YYYY-MM-DD``
        :param filing_date_lt: filter for filing date less than given value
        :param filing_date_lte: filter for filing date less than equal to given value
        :param filing_date_gt: filter for filing date greater than given value
        :param filing_date_gte: filter for filing date greater than equal to given value
        :param period_of_report_date: query by The period of report for the filing with financials data.
                                      ``datetime/date`` or string in format: ``YYY-MM-DD``.
        :param period_of_report_date_lt: filter for period of report date less than given value
        :param period_of_report_date_lte: filter for period of report date less than equal to given value
        :param period_of_report_date_gt: filter for period of report date greater than given value
        :param period_of_report_date_gte: filter for period of report date greater than equal to given value
        :param time_frame: Query by timeframe. Annual financials originate from 10-K filings, and quarterly financials
                           originate from 10-Q filings. Note: Most companies do not file quarterly reports for Q4 and
                           instead include those financials in their annual report, so some companies my not return
                           quarterly financials for Q4. See :class:`polygon.enums.StockFinancialsTimeframe` for choices.
        :param include_sources: Whether or not to include the xpath and formula attributes for each financial data
                                point. See the xpath and formula response attributes for more info. ``False`` by default
        :param order: Order results based on the sort field. 'asc' by default. See :class:`polygon.enums.SortOrder`
                      for choices.
        :param limit: number of max results to obtain. defaults to 50.
        :param sort: Sort field key used for ordering. 'filing_date' default. see
                     :class:`polygon.enums.StockFinancialsSortKey` for choices.
        :param raw_response: Whether or not to return the ``Response`` Object. Useful for when you need to say check the
                             status code or inspect the headers. Defaults to False which returns the json decoded
                             dictionary.
        :return: A JSON decoded Dictionary by default. Make ``raw_response=True`` to get underlying response object
        """

        _path = f'/vX/reference/financials'

        _data = {'ticker': ticker, 'cik': cik, 'company_name': company_name,
                 'company_name_search': company_name_search, 'sic': sic, 'filing_date': filing_date,
                 'filing_date_lt': filing_date_lt, 'filing_date_lte': filing_date_lte,
                 'filing_date_gt': filing_date_gt, 'filing_date_gte': filing_date_gte,
                 'period_of_report_date': period_of_report_date, 'period_of_report_date_lt': period_of_report_date_lt,
                 'period_of_report_date_lte': period_of_report_date_lte,
                 'period_of_report_date_gt': period_of_report_date_gt,
                 'period_of_report_date_gte': period_of_report_date_gte, 'timeframe': time_frame, 'order': order,
                 'include_sources': 'true' if include_sources else 'false', 'limit': limit, 'sort': sort}

        _res = await self._get_async_response(_path, params=_data)

        if raw_response:
            return _res

        return _res.json()

    async def async_get_stock_splits(self, symbol: str, raw_response: bool = False) -> Union[HttpxResponse, dict]:
        """
        Get a list of historical stock splits for a ticker symbol, including the execution and payment dates of the
        stock split, and the split ratio - Async method
        `Official Docs <https://polygon.io/docs/get_v2_reference_splits__stocksTicker__anchor>`__

        :param symbol: The ticker symbol of the stock/equity.
        :param raw_response: Whether or not to return the ``Response`` Object. Useful for when you need to say check the
                             status code or inspect the headers. Defaults to False which returns the json decoded
                             dictionary.
        :return: A JSON decoded Dictionary by default. Make ``raw_response=True`` to get underlying response object
        """

        _path = f'/v2/reference/splits/{symbol.upper()}'

        _res = await self._get_async_response(_path)

        if raw_response:
            return _res

        return _res.json()

    async def async_get_market_holidays(self, raw_response: bool = False) -> Union[HttpxResponse, dict]:
        """
        Get upcoming market holidays and their open/close times - Async method
        `Official Docs <https://polygon.io/docs/get_v1_marketstatus_upcoming_anchor>`__

        :param raw_response: Whether or not to return the ``Response`` Object. Useful for when you need to say check the
                             status code or inspect the headers. Defaults to False which returns the json decoded
                             dictionary.
        :return: A JSON decoded Dictionary by default. Make ``raw_response=True`` to get underlying response object
        """

        _path = '/v1/marketstatus/upcoming'

        _res = await self._get_async_response(_path)

        if raw_response:
            return _res

        return _res.json()

    async def async_get_market_status(self, raw_response: bool = False) -> Union[HttpxResponse, dict]:
        """
        Get the current trading status of the exchanges and overall financial markets - Async method
        `Official Docs <https://polygon.io/docs/get_v1_marketstatus_now_anchor>`__

        :param raw_response: Whether or not to return the ``Response`` Object. Useful for when you need to say check the
                             status code or inspect the headers. Defaults to False which returns the json decoded
                             dictionary.
        :return: A JSON decoded Dictionary by default. Make ``raw_response=True`` to get underlying response object
        """

        _path = '/v1/marketstatus/now'

        _res = await self._get_async_response(_path)

        if raw_response:
            return _res

        return _res.json()

    async def async_get_condition_mappings(self, tick_type: str = 'trades',
                                           raw_response: bool = False) -> Union[HttpxResponse, dict]:
        """
        Get a unified numerical mapping for conditions on trades and quotes. Each feed/exchange uses its own set of
        codes to identify conditions, so the same condition may have a different code depending on the originator of
        the data. Polygon.io defines its own mapping to allow for uniformly identifying a condition across
        feeds/exchanges - Async method
        `Official Docs <https://polygon.io/docs/get_v1_meta_conditions__ticktype__anchor>`__

        :param tick_type: The type of ticks to return mappings for. Defaults to 'trades'. See
                          :class:`polygon.enums.ConditionMappingTickType` for choices.
        :param raw_response: Whether or not to return the ``Response`` Object. Useful for when you need to say check the
                             status code or inspect the headers. Defaults to False which returns the json decoded
                             dictionary.
        :return: A JSON decoded Dictionary by default. Make ``raw_response=True`` to get underlying response object
        """

        _path = f'/v1/meta/conditions/{tick_type.lower()}'

        _res = await self._get_async_response(_path)

        if raw_response:
            return _res

        return _res.json()

    async def async_get_conditions(self, asset_class: str = None, data_type: str = None, id=None, sip=None, order=None,
                                   limit: int = 50, sort: str = 'name', raw_response: bool = False):
        """
        List all conditions that Polygon.io uses - Async method
        `Official Docs <https://polygon.io/docs/get_v1_meta_conditions__ticktype__anchor>`__

        :param asset_class: Filter for conditions within a given asset class. See :class:`polygon.enums.AssetClass`
                            for choices. Defaults to all assets.
        :param data_type: Filter by data type. See :class:`polygon.enums.ConditionsDataType` for choices. defaults to
                          all.
        :param id: Filter for conditions with a given ID
        :param sip: Filter by SIP. If the condition contains a mapping for that SIP, the condition will be returned.
        :param order: Order results. See :class:`polygon.enums.SortOrder` for choices.
        :param limit: limit the number of results. defaults to 50.
        :param sort: Sort field used for ordering. Defaults to 'name'. See :class:`polygon.enums.ConditionsSortKey`
                     for choices.
        :param raw_response: Whether or not to return the ``Response`` Object. Useful for when you need to say check the
                             status code or inspect the headers. Defaults to False which returns the json decoded
                             dictionary.
        :return: A JSON decoded Dictionary by default. Make ``raw_response=True`` to get underlying response object
        """
        _path = f'/vX/reference/conditions'

        _data = {'asset_class': asset_class, 'data_type': data_type, 'id': id, 'sip': sip, 'order': order,
                 'limit': limit, 'sort': sort}

        _res = await self._get_async_response(_path, params=_data)

        if raw_response:
            return _res

        return _res.json()

    async def async_get_exchanges(self, asset_class: str = None, locale: str = None, raw_response: bool = False):
        """
        List all exchanges that Polygon.io knows about - Async method
        `Official Docs <https://polygon.io/docs/get_v3_reference_exchanges_anchor>`__

        :param asset_class: filter by asset class. See :class:`polygon.enums.AssetClass` for choices.
        :param locale: Filter by locale name. See :class:`polygon.enums.Locale`
        :param raw_response: Whether or not to return the ``Response`` Object. Useful for when you need to say check the
                             status code or inspect the headers. Defaults to False which returns the json decoded
                             dictionary.
        :return: A JSON decoded Dictionary by default. Make ``raw_response=True`` to get underlying response object
        """

        _path = f'/v3/reference/exchanges'

        _data = {'asset_class': asset_class, 'locale': locale}

        _res = await self._get_async_response(_path, params=_data)

        if raw_response:
            return _res

        return _res.json()

    @staticmethod
    async def async_get_stock_exchanges(**kwargs):
        """
        DEPRECATED! Replaced by :meth:`async_get_exchanges`. This method will be removed in a future version from the library

        """
        print(f'This endpoint has been deprecated and replaced by new Exchanges endpoint. Please use get_exchanges().')
        return

    @staticmethod
    async def async_get_crypto_exchanges(**kwargs):
        """
        DEPRECATED! Replaced by :meth:`async_get_exchanges`. This method will be removed in a future version from the library

        """
        print(f'This endpoint has been deprecated and replaced by new Exchanges endpoint. Please use get_exchanges().')
        return

    async def async_get_locales(self, raw_response: bool = False) -> Union[HttpxResponse, dict]:
        """
        Get a list of locales currently supported by Polygon.io - Async method
        `Official Docs <https://polygon.io/docs/get_v2_reference_locales_anchor>`__

        :param raw_response: Whether or not to return the ``Response`` Object. Useful for when you need to say check the
                             status code or inspect the headers. Defaults to False which returns the json decoded
                             dictionary.
        :return: A JSON decoded Dictionary by default. Make ``raw_response=True`` to get underlying response object
        """

        _path = '/v2/reference/locales'

        _res = await self._get_async_response(_path)

        if raw_response:
            return _res

        return _res.json()

    async def async_get_markets(self, raw_response: bool = False) -> Union[HttpxResponse, dict]:
        """
        Get a list of markets that are currently supported by Polygon.io - Async method
        `Official Docs <https://polygon.io/docs/get_v2_reference_markets_anchor>`__

        :param raw_response: Whether or not to return the ``Response`` Object. Useful for when you need to say check the
                             status code or inspect the headers. Defaults to False which returns the json decoded
                             dictionary.
        :return: A JSON decoded Dictionary by default. Make ``raw_response=True`` to get underlying response object
        """

        _path = '/v2/reference/markets'

        _res = await self._get_async_response(_path)

        if raw_response:
            return _res

        return _res.json()


# ========================================================= #


if __name__ == '__main__':
    print('Don\'t You Dare Running Lib Files Directly')


# ========================================================= #
