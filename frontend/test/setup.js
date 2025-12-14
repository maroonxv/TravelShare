import '@testing-library/jest-dom';

// Mock window.AMap
global.window.AMap = {
    LngLat: class {
        constructor(lng, lat) {
            this.lng = lng;
            this.lat = lat;
        }
        toString() {
            return `${this.lng},${this.lat}`;
        }
    },
    Pixel: class {
        constructor(x, y) {
            this.x = x;
            this.y = y;
        }
    },
    // Mock other AMap objects if needed
};
