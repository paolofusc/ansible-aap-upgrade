#!/usr/bin/env python3
"""Fetch digest.csv from the SCP server via SFTP and look up the expected digest for an ASA image."""

import json
import sys
import paramiko


def main() -> None:
    if len(sys.argv) != 6:
        print(json.dumps({"error": "Usage: lookup_digest.py <host> <user> <password> <csv_path> <image_name>"}))
        sys.exit(1)

    host, user, password, csv_path, target_image = sys.argv[1:6]

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, username=user, password=password, timeout=15)

    try:
        sftp = client.open_sftp()
        with sftp.open(csv_path, "r") as f:
            content = f.read().decode("utf-8-sig")
        sftp.close()
    finally:
        client.close()

    found = None
    available = []

    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        sep = ";" if (";" in line and "," not in line) else ","
        parts = [p.strip() for p in line.split(sep)]
        if len(parts) < 2:
            continue
        if parts[0].lower() in ("image", "filename", "file", "name"):
            continue
        available.append(parts[0])
        if parts[0] == target_image:
            found = parts[1].lower()
            break

    print(json.dumps({"digest": found, "available": available}))


if __name__ == "__main__":
    main()
