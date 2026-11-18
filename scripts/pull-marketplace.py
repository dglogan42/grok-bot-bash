#!/usr/bin/env python3
"""Pull public Grok Bot marketplace agents into marketplace/.

Source: https://x.ai/bot/marketplace
The index page lists names and blurbs. Each agent page has the public
skills, routines, and memories. Nothing here is an install into the
Grok Bot app.
"""

import json
import re
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "marketplace"
INDEX_URL = "https://x.ai/bot/marketplace"
AGENT_URL = "https://x.ai/bot/marketplace/bots/{id}"
UA = "grok-bot-bash-marketplace-sync/1.0"

FLIGHT = re.compile(r'self\.__next_f\.push\(\[1,"(.*?)"\]\)\s*</script>', re.S)


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html"})
    with urllib.request.urlopen(req, timeout=40) as resp:
        return resp.read().decode("utf-8", "replace")


def flight_text(html):
    parts = []
    for match in FLIGHT.finditer(html):
        parts.append(json.loads('"' + match.group(1) + '"'))
    return "\n".join(parts)


def decode_value(text, needle):
    index = text.find(needle)
    if index < 0:
        raise ValueError("missing " + needle)
    obj, _ = json.JSONDecoder().raw_decode(text[index + len(needle) :])
    return obj


def decode_object(text, key):
    return decode_value(text, '"' + key + '":')


def index_templates(html):
    return decode_object(flight_text(html), "templates")


def agent_template(html):
    # The first "template" value on the page is a React slot, not the agent.
    text = flight_text(html)
    needle = '"template":{"id":'
    index = text.find(needle)
    if index < 0:
        raise ValueError("missing template")
    obj, _ = json.JSONDecoder().raw_decode(text[index + len('"template":') :])
    return obj


def pull_one(agent_id):
    last = None
    for attempt in range(3):
        try:
            html = fetch(AGENT_URL.format(id=agent_id))
            template = agent_template(html)
            if template.get("id") != agent_id:
                raise ValueError("page id " + str(template.get("id")))
            return agent_id, template, None
        except Exception as exc:
            last = exc
            time.sleep(0.4 * (attempt + 1))
    return agent_id, None, str(last)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    agents_dir = OUT / "agents"
    agents_dir.mkdir(exist_ok=True)
    listed = index_templates(fetch(INDEX_URL))
    ids = [item["id"] for item in listed]
    pulled = {}
    errors = {}
    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = [pool.submit(pull_one, agent_id) for agent_id in ids]
        for future in as_completed(futures):
            agent_id, template, error = future.result()
            if error:
                errors[agent_id] = error
                print("fail", agent_id, error)
            else:
                pulled[agent_id] = template
                print("ok", agent_id)
    index = []
    for item in listed:
        agent_id = item["id"]
        full = pulled.get(agent_id)
        path = agents_dir / (agent_id + ".json")
        if full is not None:
            path.write_text(json.dumps(full, indent=2) + "\n", encoding="utf-8")
        record = {
            "id": agent_id,
            "name": item.get("name"),
            "creatorName": item.get("creatorName"),
            "handle": item.get("handle"),
            "categories": item.get("categories") or [],
            "description": item.get("description") or "",
            "updatedAt": item.get("updatedAt"),
            "url": AGENT_URL.format(id=agent_id),
            "addHref": item.get("addHref"),
            "file": "agents/" + agent_id + ".json" if full is not None else None,
            "error": errors.get(agent_id),
        }
        index.append(record)
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    catalog = {
        "source": INDEX_URL,
        "pulledAt": stamp,
        "count": len(index),
        "saved": len(pulled),
        "errors": len(errors),
        "agents": index,
    }
    (OUT / "index.json").write_text(json.dumps(catalog, indent=2) + "\n", encoding="utf-8")
    print("saved", len(pulled), "errors", len(errors))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
