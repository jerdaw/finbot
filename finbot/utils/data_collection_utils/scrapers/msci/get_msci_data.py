from tqdm.contrib.concurrent import thread_map

from config import Config
from finbot.utils.data_collection_utils.scrapers.msci._utils import get_msci_single

MAX_THREADS = Config.MAX_THREADS


def get_msci_data(
    idx_names: str | list,
    idx_ids: str | list,
    data_frequency: str,
    check_update: bool = False,
    force_update: bool = False,
):
    if isinstance(idx_names, str) and isinstance(idx_ids, str):
        idx_names = [idx_names]
        idx_ids = [idx_ids]
    elif isinstance(idx_names, list) and isinstance(idx_ids, list):
        if len(idx_names) != len(idx_ids):
            raise ValueError("idx_names and idx_ids must have the same length.")
    else:
        raise ValueError("idx_names and idx_ids must be both str or both list.")

    return list(
        thread_map(
            lambda idx_name, idx_id: get_msci_single(
                idx_name=idx_name,
                idx_id=idx_id,
                data_frequency=data_frequency,
                check_update=check_update,
                force_update=force_update,
            ),
            idx_names,
            idx_ids,
            max_workers=MAX_THREADS,
        ),
    )


if __name__ == "__main__":
    from constants.tracked_collections.tracked_msci import TRACKED_MSCI

    names = [idx["name"] for idx in TRACKED_MSCI]
    ids = [idx["id"] for idx in TRACKED_MSCI]
    all_data = get_msci_data(idx_names=names, idx_ids=ids, data_frequency="Monthly")
    for df in all_data:
        # print first and last row
        print(df)
