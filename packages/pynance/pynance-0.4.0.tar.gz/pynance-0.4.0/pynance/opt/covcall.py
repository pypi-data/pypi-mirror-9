"""
.. Copyright (c) 2014, 2015 Marshall Farrier
   license http://opensource.org/licenses/MIT

Options - covered calls (:mod:`pynance.opt.covcall`)
======================================================

.. currentmodule:: pynance.opt.covcall
"""

from __future__ import absolute_import

import pandas as pd

from . import _constants

def get(eqprice, callprice, strike, shares=1, buycomm=0., excomm=0., dividend=0.):
    """
    Metrics for covered calls.

    Parameters
    ----------
    eqprice : float
        Price at which stock is purchased.
    callprice : float
        Price for which call is sold.
    strike : float
        Strike price of call sold.
    shares : int, optional
        Number of shares of stock. Defaults to 1.
    buycomm : float, optional
        Commission paid on total initial purchase.
    excomm : float optional
        Commission to be paid if option is exercised.
    dividend : float, optional
        Total dividends per share expected between purchase and expiration.

    Returns
    ----------
    metrics : :class:`pandas.DataFrame`
        Investment metrics

    Notes
    -----
    Cf. Lawrence McMillan, Options as a Strategic Investment, 5th ed., p. 43
    """
    _index = ['Eq Cost', 'Option Premium', 'Commission', 'Total Invested', 'Dividends', 'Eq if Ex', 
            'Comm if Ex', 'Profit if Ex', 'Ret if Ex', 'Profit if Unch', 'Ret if Unch', 'Break_Even Price',
            'Protection Pts', 'Protection Pct']
    _metrics = pd.DataFrame(index=_index, columns=['Value'])
    _shares = float(shares)
    _dividends = _shares * dividend
    _metrics.loc['Eq Cost', 'Value'] = _eqcost = _shares * eqprice
    _metrics.loc['Option Premium', 'Value'] = _optprem = _shares * callprice
    _metrics.loc['Commission', 'Value'] = float(buycomm)
    _metrics.loc['Total Invested', 'Value'] = _invested = _eqcost - _optprem + buycomm
    _metrics.loc['Dividends', 'Value'] = _dividends
    _metrics.loc['Eq if Ex', 'Value'] = _eqsale = strike * _shares
    _metrics.loc['Comm if Ex', 'Value'] = float(excomm)
    _metrics.loc['Profit if Ex', 'Value'] = _profitex = _eqsale + _dividends - _invested - excomm
    _metrics.loc['Ret if Ex', 'Value'] = round(_profitex / _invested, _constants.NDIGITS_SIG)
    _metrics.loc['Profit if Unch', 'Value'] = _profitunch = _eqcost + _dividends - _invested
    _metrics.loc['Ret if Unch', 'Value'] = round(_profitunch / _invested, _constants.NDIGITS_SIG)
    _metrics.loc['Break_Even Price', 'Value'] = _breakeven = round((_invested - _dividends) / _shares, 
            _constants.NDIGITS_SIG)
    _metrics.loc['Protection Pts', 'Value'] = _protpts = eqprice - _breakeven
    _metrics.loc['Protection Pct', 'Value'] = round(_protpts / eqprice, _constants.NDIGITS_SIG)
    return _metrics
