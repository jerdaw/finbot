from finbot.utils.data_collection_utils.bls.get_bls_data import get_bls_data


def get_bls_usa_cpi(start_date=None, end_date=None, check_update=False, force_update=False):
    return get_bls_data(
        "CUUR0000SA0",
        start_date=start_date,
        end_date=end_date,
        check_update=check_update,
        force_update=force_update,
    )


if __name__ == "__main__":
    print(get_bls_usa_cpi())
