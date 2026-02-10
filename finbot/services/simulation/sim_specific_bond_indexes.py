import pandas as pd

from finbot.services.simulation.bond_index_simulator import bond_index_simulator
from finbot.utils.data_collection_utils.google_finance.get_idcot1tr import get_idcot1tr
from finbot.utils.data_collection_utils.google_finance.get_idcot7tr import get_idcot7tr
from finbot.utils.data_collection_utils.google_finance.get_idcot20tr import get_idcot20tr


def sim_idcot20tr(
    overwrite_sim_with_index: bool = True,
    save_db: bool = True,
    force_update: bool = False,
    adj: float | None = None,
) -> pd.DataFrame:
    fund_name = "IDCOT20TR_sim"
    if overwrite_sim_with_index:
        idcot20tr_index = get_idcot20tr()
        idcot20tr_index.index = idcot20tr_index.index.normalize()
        index_closes = idcot20tr_index["Close"]
    else:
        index_closes = None

    return bond_index_simulator(
        fund_name=fund_name,
        min_maturity_years=20,
        max_maturity_years=30,
        overwrite_sim_with_index=overwrite_sim_with_index,
        index_closes=index_closes,
        save_index=save_db,
        force_update=force_update,
        additive_constant=adj if adj is not None else 7.487244839149725e-06,
    )


def sim_idcot7tr(
    overwrite_sim_with_index: bool = True,
    save_db: bool = True,
    force_update: bool = False,
    adj: float | None = None,
) -> pd.DataFrame:
    fund_name = "IDCOT7TR_sim"
    if overwrite_sim_with_index:
        idcot7tr_index = get_idcot7tr()
        idcot7tr_index.index = idcot7tr_index.index.normalize()
        index_closes = idcot7tr_index["Close"]
    else:
        index_closes = None

    return bond_index_simulator(
        fund_name=fund_name,
        min_maturity_years=7,
        max_maturity_years=10,
        overwrite_sim_with_index=overwrite_sim_with_index,
        index_closes=index_closes,
        save_index=save_db,
        force_update=force_update,
        additive_constant=adj if adj is not None else -4.415524686042451e-06,
    )


def sim_idcot1tr(
    overwrite_sim_with_index: bool = True,
    save_db: bool = True,
    force_update: bool = False,
    adj: float | None = None,
) -> pd.DataFrame:
    fund_name = "IDCOT1TR_sim"
    if overwrite_sim_with_index:
        idcot1tr_index = get_idcot1tr()
        idcot1tr_index.index = idcot1tr_index.index.normalize()
        index_closes = idcot1tr_index["Close"]
    else:
        index_closes = None

    return bond_index_simulator(
        fund_name=fund_name,
        min_maturity_years=1,
        max_maturity_years=3,
        overwrite_sim_with_index=overwrite_sim_with_index,
        index_closes=index_closes,
        save_index=save_db,
        force_update=force_update,
        additive_constant=adj if adj is not None else -9.373680305836604e-06,
    )
