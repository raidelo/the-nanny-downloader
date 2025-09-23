from pathlib import Path
import re

TEMPLATE_URL = "https://retrotve.com/?trdownload=%(trdownload)s&trid=%(trid)s"
DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36>"
CHAPTER_MATCH = re.compile(r"^(\d)x(\d{1,2})$")
TRID_MAPPING_PATH = Path(__file__).with_name("the-nanny-trid-mapping.json")
