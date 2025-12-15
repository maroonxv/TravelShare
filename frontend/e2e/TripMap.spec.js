import { test, expect } from '@playwright/test';

test.describe('TripMap Component E2E', () => {
    test.beforeEach(async ({ page }) => {
        // Inject test mode flag
        await page.addInitScript(() => {
            window.__TEST_MODE__ = true;
        });
    });

  test('should render map and markers with correct coordinates', async ({ page }) => {
    // Debug: Print page content if it fails
    page.on('console', msg => console.log('PAGE LOG:', msg.text()));

    await page.goto('/test/trip-map');

    // 1. Wait for map container to be visible
    // Wait for ANY content first to see if page loads at all
    try {
        await expect(page.locator('body')).toBeVisible();
        await expect(page.locator('[data-testid="trip-map-page-root"]')).toBeVisible({ timeout: 5000 });
    } catch (e) {
        console.log('Current URL:', page.url());
        console.log('Page content:', await page.content());
        throw e;
    }

    await expect(page.locator('[data-testid="trip-map-container"]').first()).toBeVisible();

    // Debug: Poll for state visibility
    for (let i = 0; i < 5; i++) {
        const state = await page.evaluate(() => ({
            hasAMap: !!window.AMap,
            hasInstance: !!window.__TEST_MAP_INSTANCE__
        }));
        console.log(`DEBUG Poll ${i}:`, state);
        if (state.hasInstance) break;
        await page.waitForTimeout(1000);
    }

    // 2. Wait for AMap script to load and instance to be created
    // We poll window.__TEST_MAP_INSTANCE__ which we exposed in TripMap.jsx
    await expect.poll(async () => {
      return await page.evaluate(() => !!window.__TEST_MAP_INSTANCE__);
    }, {
      message: 'Map instance was not created within timeout',
      timeout: 15000 
    }).toBe(true);

    // 3. Verify Map Center (should be first activity: 121.5, 31.2)
    const center = await page.evaluate(() => {
        const map = window.__TEST_MAP_INSTANCE__;
        const center = map.getCenter();
        return { lng: center.getLng(), lat: center.getLat() };
    });
    
    expect(center.lng).toBeCloseTo(121.5, 4);
    expect(center.lat).toBeCloseTo(31.2, 4);

    // 4. Verify Markers
    // Wait for markers to be populated
    await expect.poll(async () => {
        return await page.evaluate(() => window.__TEST_MARKERS__ && window.__TEST_MARKERS__.length);
    }, {
        message: 'Markers were not populated',
        timeout: 5000
    }).toBe(2);

    const markersData = await page.evaluate(() => {
        return window.__TEST_MARKERS__.map(m => {
            // Note: TripMap.jsx constructs objects with 'position' property which is an AMap.LngLat
            // The markers array in TripMap.jsx state contains config objects, NOT AMap.Marker instances directly if using <Marker /> component
            // However, looking at TripMap.jsx: 
            // const markers = useMemo(...) returns array of objects { position: ..., title: ... }
            // So we are validating the PROPS passed to the Marker components, which have been processed by our logic.
            
            // Wait, window.__TEST_MARKERS__ is the state variable 'markers' from TripMap.jsx
            // Let's verify what 'markers' contains.
            // It contains objects with 'position' property which is AMap.LngLat instance.
            return {
                lng: m.position.getLng(),
                lat: m.position.getLat(),
                title: m.title
            };
        });
    });

    // Activity 1: String inputs "121.5", "31.2" -> Should be parsed to numbers
    expect(markersData[0].lng).toBe(121.5);
    expect(markersData[0].lat).toBe(31.2);
    expect(markersData[0].title).toBe('Test Activity 1');

    // Activity 2: Number inputs 121.6, 31.3
    expect(markersData[1].lng).toBe(121.6);
    expect(markersData[1].lat).toBe(31.3);
    expect(markersData[1].title).toBe('Test Activity 2');
  });
});
