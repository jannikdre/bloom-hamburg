// Handgeschriebener Service Worker (ersetzt vite-plugin-pwa/workbox wegen
// Node-19-Inkompatibilität). Liefert Offline-Fähigkeit über Runtime-Caching –
// kein Precache-Manifest nötig, daher unabhängig von gehashten Build-Dateinamen.
const VERSION = "v1";
const SHELL_CACHE = `bloom-shell-${VERSION}`;
const DATA_CACHE = `bloom-data-${VERSION}`;
const IMG_CACHE = `bloom-images-${VERSION}`;

self.addEventListener("install", () => {
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    (async () => {
      const keep = [SHELL_CACHE, DATA_CACHE, IMG_CACHE];
      const keys = await caches.keys();
      await Promise.all(keys.filter((k) => !keep.includes(k)).map((k) => caches.delete(k)));
      await self.clients.claim();
    })()
  );
});

self.addEventListener("fetch", (event) => {
  const req = event.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);

  // current.json: stale-while-revalidate → letzte Daten offline, neue im Hintergrund.
  if (url.pathname.endsWith("data/current.json")) {
    event.respondWith(staleWhileRevalidate(req, DATA_CACHE));
    return;
  }

  // Navigations-Requests (App-Shell): network-first, Fallback auf gecachte index.html.
  if (req.mode === "navigate") {
    event.respondWith(
      (async () => {
        try {
          const fresh = await fetch(req);
          const cache = await caches.open(SHELL_CACHE);
          cache.put(req, fresh.clone());
          return fresh;
        } catch {
          const cache = await caches.open(SHELL_CACHE);
          return (await cache.match(req)) || (await cache.match("./")) || Response.error();
        }
      })()
    );
    return;
  }

  // Cross-Origin Bilder (z. B. Wikimedia): cache-first.
  if (req.destination === "image") {
    event.respondWith(cacheFirst(req, IMG_CACHE));
    return;
  }

  // Same-Origin Static Assets (js/css/png/icons): cache-first.
  if (url.origin === self.location.origin) {
    event.respondWith(cacheFirst(req, SHELL_CACHE));
  }
});

async function cacheFirst(req, cacheName) {
  const cache = await caches.open(cacheName);
  const cached = await cache.match(req);
  if (cached) return cached;
  const fresh = await fetch(req);
  if (fresh.ok) cache.put(req, fresh.clone());
  return fresh;
}

async function staleWhileRevalidate(req, cacheName) {
  const cache = await caches.open(cacheName);
  const cached = await cache.match(req);
  const network = fetch(req)
    .then((res) => {
      if (res.ok) cache.put(req, res.clone());
      return res;
    })
    .catch(() => cached);
  return cached || network;
}
