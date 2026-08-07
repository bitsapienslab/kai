self.addEventListener('install', event => event.waitUntil(
  caches.open('rise-v12').then(cache => cache.addAll([
    './',
    'index.html',
    'css/rise.css',
    'js/api.js',
    'js/app.js',
    'assets/backgrounds/world-main.png',
    'assets/backgrounds/world-social.png',
    'assets/backgrounds/world-learning.png',
    'assets/backgrounds/world-alt.png',
    'assets/kai-portrait.png',
    'assets/action-card-bg.png',
    'manifest.webmanifest',
    'icon.svg'
  ]))
));
self.addEventListener('activate', event => event.waitUntil(
  caches.keys().then(keys => Promise.all(
    keys.filter(k => k !== 'rise-v12').map(k => caches.delete(k))
  ))
));
self.addEventListener('fetch', event => event.respondWith(
  caches.match(event.request).then(cached => cached || fetch(event.request))
));
self.addEventListener('push', event => {
  const data = event.data?.json?.() || { title: 'RISE', body: 'You have an action to review.' };
  event.waitUntil(self.registration.showNotification(data.title, {
    body: data.body,
    icon: './icon.svg',
    badge: './icon.svg'
  }));
});
self.addEventListener('notificationclick', event => {
  event.notification.close();
  event.waitUntil(clients.openWindow('./'));
});
