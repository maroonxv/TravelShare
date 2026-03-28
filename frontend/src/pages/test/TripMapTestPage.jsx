import React from 'react';
import TripMap from '../travel/TripMap';

// Hardcoded test data to ensure stability
const TEST_ACTIVITIES = [
    {
        name: 'Test Activity 1',
        location: { longitude: '121.5', latitude: '31.2' } // String coordinates
    },
    {
        name: 'Test Activity 2',
        location: { longitude: 121.6, latitude: 31.3 } // Number coordinates
    }
];

const TEST_TRANSITS = [
    {
        mode: 'walking',
        polyline: '121.5,31.2;121.6,31.3'
    }
];

const TripMapTestPage = () => {
    console.log('Rendering TripMapTestPage');
    return (
        <div style={{ padding: '20px' }} data-testid="trip-map-page-root">
            <h1>TripMap E2E Test Page</h1>
            <div data-testid="trip-map-container" style={{ width: '800px', height: '600px', border: '2px solid red' }}>
                <TripMap 
                    activities={TEST_ACTIVITIES} 
                    transits={TEST_TRANSITS}
                />
            </div>
            
            <div data-testid="test-data-display">
                <pre>{JSON.stringify({ activities: TEST_ACTIVITIES, transits: TEST_TRANSITS }, null, 2)}</pre>
            </div>
        </div>
    );
};

export default TripMapTestPage;
