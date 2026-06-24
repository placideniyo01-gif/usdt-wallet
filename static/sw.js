const CACHE_NAME = "usdt-wallet-v2";

self.addEventListener("install", event => {

    self.skipWaiting();

    event.waitUntil(

        caches.open(CACHE_NAME)
        .then(cache => {

            return cache.addAll([
                "/"
            ]);

        })

    );

});

self.addEventListener("activate", event => {

    event.waitUntil(
        self.clients.claim()
    );

});

self.addEventListener("fetch", event => {

    event.respondWith(

        caches.match(event.request)
        .then(response => {

            return response || fetch(event.request);

        })

    );

});