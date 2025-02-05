import jsVectorMap from 'jsvectormap';
import 'jsvectormap/dist/maps/world.js';

document.addEventListener('DOMContentLoaded', function() {
    const map = new jsVectorMap({
        selector: '#map',
        map: 'world',
        markers: [
            { name: 'New York', coords: [40.7128, -74.0060] },
            { name: 'London', coords: [51.5074, -0.1278] },
            { name: 'Shanghai', coords: [31.2304, 121.4737] },
            { name: 'Tokyo', coords: [35.6762, 139.6503] },
            { name: 'Singapore', coords: [1.3521, 103.8198] },
            { name: 'Mumbai', coords: [19.0760, 72.8777] },  // Added Mumbai, India
            { name: 'Stockholm', coords: [59.3293, 18.0686] },  // Added Stockholm, Sweden
            { name: 'Johannesburg', coords: [-26.2041, 28.0473] }  // Added Johannesburg, South Africa
        ],
        markerStyle: {
            initial: {
                fill: '#34D399'
            }
        },
        zoomOnScroll: true,
        zoomButtons: true
    });
});