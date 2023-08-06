"""
.. Copyright (c) 2015 Marshall Farrier
   license http://opensource.org/licenses/MIT

Options - remote retrieval (:mod:`pynance.opt.retrieve`)
=========================================================

.. currentmodule:: pynance.opt.retrieve
"""

from __future__ import absolute_import

import pandas_datareader as pdr

from .core import Options

def get(equity, showinfo=True):
    """
    Retrieve all current options chains for given equity.

    Parameters
    -------------
    equity : str
        Equity for which to retrieve options data.

    Returns
    -------------
    optdata : :class:`~pynance.opt.core.Options`
        All options data for given equity currently available
        from Yahoo! Finance.
        
    Raises
    ------
    pandas.io.data.RemoteDataError
        If remote data is not available, as is often the case at night
        when Yahoo! is resetting its servers in preparation for the
        next session.
        
    Examples
    -------------
    Basic usage::
    
    >>> fopt = pn.opt.get('f')

    To show useful information (expiration dates, stock price, quote time)
    when retrieving options data, you can chain the call to
    :func:`get` with :meth:`~pynance.opt.core.Options.info`::
    
        >>> fopt = pn.opt.get('f').info()
        Expirations:
        ...
        Stock: 15.93
        Quote time: 2015-03-07 16:00
    """
    _optmeta = pdr.data.Options(equity, 'yahoo')
    _optdata = None
    try:
        _optdata = _optmeta.get_all_data()
    except (AttributeError, ValueError, pdr.data.RemoteDataError):
        raise pdr.data.RemoteDataError(
                "No options data available for '{}'".format(equity))
    return Options(_optdata)
