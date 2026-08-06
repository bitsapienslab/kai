self.addEventListener('install', event => event.waitUntil(caches.open('bussola-v1').then(cache => cache.addAll(['./','index.html','styles.css','ui.css','liquid.css','app.js','manifest.webmanifest','icon.svg']))));
self.addEventListener('fetch', event => event.respondWith(caches.match(event.request).then(cached => cached || fetch(event.request))));
self.addEventListener('push', event => { const data = event.data?.json?.() || {title:'Bússola',body:'Tens uma ação para rever.'}; event.waitUntil(self.registration.showNotification(data.title,{body:data.body,icon:'./icon.svg',badge:'./icon.svg'})); });
self.addEventListener('notificationclick', event => { event.notification.close(); event.waitUntil(clients.openWindow('./')); });
