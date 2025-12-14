import { render, waitFor, screen } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import React from 'react';
import TripMap from '../../src/pages/travel/TripMap';

// Global mock variables to capture instance methods
const mockSetFitView = vi.fn();
const mockSetCenter = vi.fn();

// Mock @uiw/react-amap
vi.mock('@uiw/react-amap', () => {
    return {
        APILoader: ({ children, onComplete }) => {
            React.useEffect(() => {
                // Simulate script loading delay
                setTimeout(() => {
                    onComplete && onComplete();
                }, 10);
            }, []);
            return <div>{children}</div>;
        },
        Map: ({ children, onInstanceCreated, center }) => {
            React.useEffect(() => {
                const mockInstance = {
                    setFitView: mockSetFitView,
                    setCenter: mockSetCenter,
                    destroy: vi.fn(),
                };
                onInstanceCreated && onInstanceCreated(mockInstance);
            }, []);
            
            return (
                <div data-testid="amap-map" data-center={center ? center.join(',') : 'undefined'}>
                    {children}
                </div>
            );
        },
        Marker: () => <div data-testid="amap-marker" />,
        Polyline: () => <div data-testid="amap-polyline" />,
        ToolBarControl: () => null,
        ScaleControl: () => null,
        ControlBarControl: () => null,
    };
});

describe('TripMap Component', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        // Reset window.AMap mock just in case
        window.AMap = {
            LngLat: class {
                constructor(lng, lat) {
                    this.lng = lng;
                    this.lat = lat;
                }
            },
            Pixel: class {
                constructor(x, y) {}
            }
        };
    });

    it('should center the map on the first activity location even if coordinates are strings', async () => {
        const activities = [
            {
                name: 'Activity 1',
                location: { longitude: '121.5', latitude: '31.2' } // Strings from JSON
            },
            {
                name: 'Activity 2',
                location: { longitude: '121.6', latitude: '31.3' }
            }
        ];

        render(<TripMap activities={activities} transits={[]} />);

        // Expect numbers in setCenter call
        await waitFor(() => {
            expect(mockSetCenter).toHaveBeenCalledWith([121.5, 31.2]);
        });
    });

    it('should call setFitView after loading', async () => {
         const activities = [
            {
                name: 'Activity 1',
                location: { longitude: 121.5, latitude: 31.2 }
            }
        ];
        
        render(<TripMap activities={activities} transits={[]} />);

        // setFitView is called with a delay (800ms in current code)
        await waitFor(() => {
            expect(mockSetFitView).toHaveBeenCalled();
        }, { timeout: 2000 });
    });

    it('should handle empty activities gracefully', async () => {
        render(<TripMap activities={[]} transits={[]} />);
        
        await waitFor(() => {
            const mapEl = screen.getByTestId('amap-map');
            expect(mapEl).toHaveAttribute('data-center', 'undefined');
        });
        
        expect(mockSetCenter).not.toHaveBeenCalled();
    });
});
