from __future__ import annotations

import re
import logging

logger = logging.getLogger(__name__)

# Matches lines like:
#   TX SNR:12.5 RSSI:-45 Score:0.85 Hash:ABCD1234 Path:direct
#   RX SNR:8.2 RSSI:-67 Score:0.72 Hash:EF567890 Path:node1>node2
_PACKET_RE = re.compile(
    r"(TX|RX)\s+"
    r"SNR:([-\d.]+)\s+"
    r"RSSI:([-\d.]+)"
    r"(?:\s+Score:([-\d.]+))?"
    r"(?:\s+Hash:(\w+))?"
    r"(?:\s+Path:(.+))?"
)


def parse_packet_line(line: str) -> dict | None:
    m = _PACKET_RE.search(line)
    if not m:
        return None

    return {
        "direction": m.group(1),
        "snr": float(m.group(2)),
        "rssi": float(m.group(3)),
        "score": float(m.group(4)) if m.group(4) else None,
        "hash": m.group(5),
        "path": m.group(6).strip() if m.group(6) else None,
    }
