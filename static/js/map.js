var NeighborMap = (function () {
    var map = null;
    var markers = [];

    function init(el) {
        map = L.map(el).setView([0, 0], 2);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; OpenStreetMap contributors',
            maxZoom: 18,
        }).addTo(map);
        return map;
    }

    function update(neighbors) {
        if (!map) return;

        // Remove old markers
        markers.forEach(function (m) { map.removeLayer(m); });
        markers = [];

        var bounds = [];

        neighbors.forEach(function (n) {
            if (n.lat == null || n.lon == null) return;
            if (n.lat === 0 && n.lon === 0) return;

            var marker = L.marker([n.lat, n.lon]).addTo(map);
            var ago = timeSince(n.last_seen);
            marker.bindPopup(
                '<strong>' + (n.name || n.pubkey_prefix) + '</strong><br>' +
                'SNR: ' + (n.last_snr != null ? n.last_snr + ' dB' : '--') + '<br>' +
                'Last seen: ' + ago
            );
            markers.push(marker);
            bounds.push([n.lat, n.lon]);
        });

        if (bounds.length > 0) {
            map.fitBounds(bounds, { padding: [30, 30], maxZoom: 14 });
        }
    }

    function timeSince(epochSecs) {
        if (!epochSecs) return 'unknown';
        var diff = Math.floor(Date.now() / 1000) - epochSecs;
        if (diff < 60) return diff + 's ago';
        if (diff < 3600) return Math.floor(diff / 60) + 'm ago';
        if (diff < 86400) return Math.floor(diff / 3600) + 'h ago';
        return Math.floor(diff / 86400) + 'd ago';
    }

    function invalidateSize() {
        if (map) map.invalidateSize();
    }

    return { init: init, update: update, invalidateSize: invalidateSize };
})();
