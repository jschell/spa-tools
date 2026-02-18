#!/usr/bin/env node
// Fetches F1 RSS feeds via rss2json.com and writes news-cache.json to the repo root.
// Runs as part of the update-f1-news GitHub Actions workflow.
// Uses only built-in Node.js modules — no npm install required.

'use strict';

const https = require('https');
const fs = require('fs');
const path = require('path');

const RSS2JSON_BASE = 'https://api.rss2json.com/v1/api.json?rss_url=';
const OUTPUT_PATH = path.join(__dirname, '..', '..', 'news-cache.json');
const TIMEOUT_MS = 15000;
const MAX_ITEMS = 60;

const FEEDS = [
  { key: 'f1-official',   name: 'Formula 1',     url: 'https://www.formula1.com/en/latest/all.xml' },
  { key: 'bbc-f1',        name: 'BBC Sport',      url: 'https://feeds.bbci.co.uk/sport/formula1/rss.xml' },
  { key: 'autosport',     name: 'Autosport',      url: 'https://www.autosport.com/rss/f1/news' },
  { key: 'motorsport',    name: 'Motorsport.com', url: 'https://www.motorsport.com/rss/f1/news/' },
  { key: 'racingnews365', name: 'RacingNews365',  url: 'https://racingnews365.com/feed/news.xml' },
  { key: 'racer',         name: 'RACER',          url: 'https://racer.com/f1/feed/' },
];

function get(url) {
  return new Promise((resolve, reject) => {
    const req = https.get(url, { timeout: TIMEOUT_MS }, (res) => {
      if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
        // Follow one redirect
        return get(res.headers.location).then(resolve).catch(reject);
      }
      if (res.statusCode !== 200) {
        res.resume();
        return reject(new Error(`HTTP ${res.statusCode} for ${url}`));
      }
      let body = '';
      res.setEncoding('utf8');
      res.on('data', chunk => { body += chunk; });
      res.on('end', () => resolve(body));
    });
    req.on('error', reject);
    req.on('timeout', () => { req.destroy(); reject(new Error(`Timeout fetching ${url}`)); });
  });
}

async function fetchFeed(feed) {
  const apiUrl = RSS2JSON_BASE + encodeURIComponent(feed.url);
  const body = await get(apiUrl);
  const json = JSON.parse(body);
  if (json.status !== 'ok') throw new Error(`rss2json error for ${feed.key}: ${json.message}`);
  return (json.items ?? []).map(item => ({
    title: item.title ?? '',
    link: item.link ?? '',
    source: feed.name,
    pubDate: item.pubDate ?? '',
    summary: item.description ?? '',
    imageUrl: item.thumbnail || item.enclosure?.thumbnail || null,
  }));
}

async function main() {
  const results = await Promise.allSettled(FEEDS.map(fetchFeed));

  const allItems = [];
  for (let i = 0; i < FEEDS.length; i++) {
    const r = results[i];
    if (r.status === 'fulfilled') {
      allItems.push(...r.value);
    } else {
      console.warn(`Failed to fetch ${FEEDS[i].key}: ${r.reason?.message}`);
    }
  }

  if (allItems.length === 0) {
    console.error('All feeds failed — keeping existing cache.');
    process.exit(0);
  }

  // Sort descending by pubDate, deduplicate by title+source, cap at MAX_ITEMS
  allItems.sort((a, b) => new Date(b.pubDate) - new Date(a.pubDate));
  const seen = new Set();
  const deduped = allItems.filter(item => {
    const key = item.title.toLowerCase().trim();
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  }).slice(0, MAX_ITEMS);

  fs.writeFileSync(OUTPUT_PATH, JSON.stringify(deduped, null, 2) + '\n', 'utf8');
  console.log(`Wrote ${deduped.length} items to news-cache.json`);
}

main().catch(err => { console.error(err); process.exit(1); });
