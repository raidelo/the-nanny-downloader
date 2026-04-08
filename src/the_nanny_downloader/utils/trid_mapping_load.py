import json
from typing import Any

from the_nanny_downloader.constants import TRID_MAPPING_PATH
from the_nanny_downloader.errors import (
    InvalidTRIDMappingFileFormat,
)


def _validate_trid_mapping_file_format(data: Any) -> dict[str, int]:
    if not isinstance(data, dict):
        raise InvalidTRIDMappingFileFormat(TRID_MAPPING_PATH)
    for k, v in data.items():
        if not isinstance(k, str) or not isinstance(v, int):
            raise InvalidTRIDMappingFileFormat(TRID_MAPPING_PATH)
    return data


def load_trid_mapping() -> dict[str, int]:
    with open(TRID_MAPPING_PATH, "rb") as jsonfile:
        data = json.load(jsonfile)

        return _validate_trid_mapping_file_format(data)
