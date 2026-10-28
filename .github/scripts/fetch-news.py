#!/usr/bin/env python3
"""Refresh the news cache from publishers' RSS/Atom feeds (stdlib only)."""
import concurrent.futures
import email.utils
import json
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FEEDS = [
    ('Formula 1', 'https://www.formula1.com/en/latest/all.xml'),
    ('BBC Sport', 'https://feeds.bbci.co.uk/sport/formula1/rss.xml'),
    ('Autosport', 'https://www.autosport.com/rss/f1/news'),
    ('Motorsport.com', 'https://www.motorsport.com/rss/f1/news/'),
    ('RacingNews365', 'https://racingnews365.com/feed/news.xml'),
    ('RACER', 'https://racer.com/f1/feed/'),
]
ATOM = '{http://www.w3.org/2005/Atom}'


def iso_date(value):
    if not value:
        return None
    try:
        date = datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError:
        try:
            date = email.utils.parsedate_to_datetime(value)
        except (ValueError, TypeError):
            return None
    return date.replace(tzinfo=date.tzinfo or timezone.utc).astimezone(timezone.utc).isoformat()


def parse_feed(body, source):
    root = ET.fromstring(body)
    atom = root.tag == ATOM + 'feed'
    entries = root.findall(ATOM + 'entry') if atom else root.findall('./channel/item')
    items = []
    for entry in entries:
        def text(*names):
            for name in names:
                node = entry.find(name)
                if node is not None:
                    value = ''.join(node.itertext()).strip()
                    if value:
                        return value
            return ''
        title = text(ATOM + 'title' if atom else 'title')
        if atom:
            link = next((n.get('href', '') for n in entry.findall(ATOM + 'link')
                         if n.get('rel', 'alternate') == 'alternate'), '')
            date = text(ATOM + 'published', ATOM + 'updated')
            summary = text(ATOM + 'summary', ATOM + 'content')
        else:
            link, summary = text('link'), text('description', '{http://purl.org/rss/1.0/modules/content/}encoded')
            date = text('pubDate', '{http://purl.org/dc/elements/1.1/}date', '{https://purl.org/dc/elements/1.1/}date')
        published = iso_date(date)
        # Never manufacture publication dates for undated articles.
        if not title or not link.startswith(('https://', 'http://')) or not published:
            continue
        image = next((n.get('url') for n in entry.iter()
                      if n.tag in ('{http://search.yahoo.com/mrss/}thumbnail', '{http://search.yahoo.com/mrss/}content', 'enclosure')
                      and n.get('url', '').startswith(('https://', 'http://'))
                      and (n.tag != 'enclosure' or n.get('type', '').startswith('image/'))), None)
        items.append(dict(title=title, link=link, source=source, pubDate=published,
                          summary=summary, imageUrl=image))
    if not items:
        raise ValueError('No usable dated articles in feed')
    return items


def fetch_feed(feed):
    source, url = feed
    request = urllib.request.Request(url, headers={
        'User-Agent': 'spa-tools-news/1.0 (+https://github.com/jschell/spa-tools)',
        'Accept': 'application/rss+xml, application/atom+xml, application/xml, text/xml',
    })
    with urllib.request.urlopen(request, timeout=20) as response:
        return parse_feed(response.read(), source)


def main():
    items, failed = [], []
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        futures = {pool.submit(fetch_feed, feed): feed[0] for feed in FEEDS}
        for future in concurrent.futures.as_completed(futures):
            source = futures[future]
            try:
                result = future.result()
                items.extend(result)
                print(f'{source}: {len(result)} articles')
            except Exception as error:
                failed.append(source)
                print(f'::warning::{source}: {error}', file=sys.stderr)
    if not items:
        print('::error::All feeds failed; existing cache preserved.', file=sys.stderr)
        return 1
    items.sort(key=lambda item: item['pubDate'], reverse=True)
    seen, unique = set(), []
    for item in items:
        key = item['title'].strip().casefold()
        if key not in seen:
            seen.add(key)
            unique.append(item)
    payload = dict(updatedAt=datetime.now(timezone.utc).isoformat(),
                   failedSources=sorted(failed), items=unique[:120])
    output = ROOT / 'f1-tracker-news-cache.json'
    temporary = output.with_suffix('.tmp')
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n')
    temporary.replace(output)
    print(f'Wrote {len(payload["items"])} articles; {len(failed)} failed sources')
    return 0


if __name__ == '__main__':
    sys.exit(main())
