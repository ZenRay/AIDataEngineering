#!/usr/bin/env python3
"""Check common MCP credential patterns without printing configuration values."""
import json
import re
import sys
from pathlib import Path
from urllib.parse import parse_qsl, urlsplit

SENSITIVE = {"password", "passwd", "pwd", "secret", "apikey", "token", "authorization", "clientsecret", "accesstoken", "refreshtoken", "xapikey", "xauthtoken", "privatekey", "bearertoken"}
PLACEHOLDER = re.compile(r"^(?:Bearer\s+)?\$\{[A-Za-z_][A-Za-z0-9_]*\}$", re.IGNORECASE)


def normalized(value):
    return re.sub(r"[^a-z0-9]", "", value.lower())


def inspect(value):
    findings = set()

    def visit(node):
        if isinstance(node, dict):
            for key, child in node.items():
                if normalized(key) in SENSITIVE:
                    if not isinstance(child, str) or not PLACEHOLDER.fullmatch(child):
                        findings.add("credential field requires review")
                if normalized(key) == "url" and isinstance(child, str):
                    try:
                        url = urlsplit(child)
                        if url.username is not None or url.password is not None:
                            findings.add("URL user information requires review")
                        if any(normalized(k) in SENSITIVE for k, _ in parse_qsl(url.query, keep_blank_values=True)):
                            findings.add("credential query parameter requires review")
                    except ValueError:
                        findings.add("URL format requires review")
                visit(child)
        elif isinstance(node, list):
            for child in node:
                visit(child)

    visit(value)
    return sorted(findings)


def reject_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key")
        result[key] = value
    return result


def main(argv):
    if len(argv) != 2:
        print("Usage: check-mcp-config.py <configuration-file>", file=sys.stderr)
        return 2
    try:
        with Path(argv[1]).open(encoding="utf-8") as source:
            config = json.load(source, object_pairs_hook=reject_duplicate_keys)
    except (OSError, UnicodeError, ValueError, RecursionError):
        print("MCP configuration could not be read or parsed; manual review required.")
        return 2
    if not isinstance(config, dict):
        print("MCP configuration must be a JSON object; manual review required.")
        return 2
    try:
        findings = inspect(config)
    except RecursionError:
        print("MCP configuration nesting exceeds inspection limit; manual review required.")
        return 2
    if findings:
        for item in findings:
            print(item)
        print("Common credential pattern needs review; no values were printed.")
        return 1
    print("No common credential patterns detected; this is not proof of safety.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
