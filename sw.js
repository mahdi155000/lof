from flask import send_from_directory

@app.route('/sw.js')
def sw():
    return send_from_directory('.', 'sw.js')

const CACHE_NAME = 'lof-cache-v1';
const urlsToCache = [
  '/',
  '/static/style.css', // add your CSS or JS files if any
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => response || fetch(event.request))
  );
});