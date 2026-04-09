var staticCacheName = "hangarin-v1";
var filesToCache = [
    '/',
    '/static/css/output.css', // Ensure this matches your CSS filename
];

// Cache on install
self.addEventListener("install", event => {
    this.skipWaiting();
    event.waitUntil(
        caches.open(staticCacheName).then(cache => {
            return cache.addAll(filesToCache);
        })
    );
});

// Clear old caches
self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.filter(cacheName => (cacheName !== staticCacheName))
                .map(cacheName => caches.delete(cacheName))
            );
        })
    );
});

// Serve from cache, fallback to network
self.addEventListener("fetch", event => {
    event.respondWith(
        caches.match(event.request).then(response => {
            return response || fetch(event.request);
        }).catch(() => {
            return caches.match('/');
        })
    );
});