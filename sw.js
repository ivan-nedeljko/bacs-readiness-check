// Offline-Speicher der App: online immer die neueste Fassung, offline die zuletzt geladene.
var CACHE = 'rc-1.0.2';
var DATEIEN = ['./', 'index.html', 'app.css', 'app.js', 'katalog.js', 'manifest.webmanifest', 'icon.svg'];
self.addEventListener('install', function (e) { e.waitUntil(caches.open(CACHE).then(function (c) { return c.addAll(DATEIEN); })); self.skipWaiting(); });
self.addEventListener('activate', function (e) {
  e.waitUntil(caches.keys().then(function (ks) { return Promise.all(ks.filter(function (k) { return k !== CACHE; }).map(function (k) { return caches.delete(k); })); }));
  self.clients.claim();
});
self.addEventListener('fetch', function (e) {
  if (e.request.method !== 'GET') return;
  e.respondWith(fetch(e.request).then(function (r) {
    var kopie = r.clone(); caches.open(CACHE).then(function (c) { c.put(e.request, kopie); }); return r;
  }).catch(function () { return caches.match(e.request).then(function (r) { return r || caches.match('index.html'); }); }));
});
