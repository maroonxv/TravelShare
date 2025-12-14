import sys
import os
import time
from datetime import datetime, timedelta, date
import random

# Add backend/src to path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(os.path.dirname(current_dir))
backend_src = os.path.join(backend_dir, 'src')
sys.path.append(backend_src)
print(f"Added {backend_src} to sys.path")

from app import create_app
from shared.database.core import SessionLocal
from app_travel.infrastructure.database.persistent_model.trip_po import TripPO, TripDayPO, ActivityPO, TransitPO
from app_travel.infrastructure.external_service.gaode_geo_service_impl import GaodeGeoServiceImpl
from app_travel.domain.value_objects.travel_value_objects import Location
from sqlalchemy import asc
import uuid

def generate_uuid():
    return str(uuid.uuid4())

def add_routes():
    print("Starting route calculation...")
    session = SessionLocal()
    geo_service = GaodeGeoServiceImpl()

    try:
        # Get all trips
        trips = session.query(TripPO).all()
        print(f"Found {len(trips)} trips.")

        for trip in trips:
            print(f"Processing trip: {trip.name}")
            # Get all days for the trip
            days = session.query(TripDayPO).filter_by(trip_id=trip.id).order_by(asc(TripDayPO.day_number)).all()
            
            for day in days:
                print(f"  Processing Day {day.day_number}")
                # Get all activities for the day
                activities = session.query(ActivityPO).filter_by(trip_day_id=day.id).order_by(asc(ActivityPO.start_time)).all()
                
                if len(activities) < 2:
                    continue
                
                for i in range(len(activities) - 1):
                    current_act = activities[i]
                    next_act = activities[i+1]
                    
                    print(f"    Calculating route from '{current_act.name}' to '{next_act.name}'...")
                    
                    # Create Location objects
                    origin = Location(name=current_act.location_name)
                    destination = Location(name=next_act.location_name)
                    
                    # Determine mode based on distance (rough estimate first) or random logic
                    # Or just try different modes. Let's default to 'driving' or 'transit'
                    # Since it's a travel app, 'transit' (public transport) or 'driving' (taxi/car) are common.
                    # Let's try to be smart: if short distance use walking?
                    # For now, let's stick to a mix or default to driving/transit.
                    # Let's use driving for simplicity and reliability of API, or transit for city travel.
                    # Given the detailed city locations, 'transit' or 'driving' makes sense.
                    
                    # We need to geocode first to get coordinates for accurate distance, 
                    # but get_route does geocoding internally if needed.
                    
                    mode = random.choice(["driving", "transit"])
                    
                    # Call Geo Service
                    route_info = geo_service.get_route(origin, destination, mode=mode)
                    
                    if not route_info or not route_info.get("paths"):
                        print(f"      Warning: No route found for {origin.name} -> {destination.name} via {mode}. Trying driving...")
                        mode = "driving"
                        route_info = geo_service.get_route(origin, destination, mode=mode)
                    
                    if route_info and route_info.get("paths"):
                        # Take the first path
                        path = route_info["paths"][0]
                        distance = path.get("distance", 0) # meters
                        duration = path.get("duration", 0) # seconds
                        
                        # Convert to minutes
                        duration_minutes = int(duration / 60)
                        
                        # Create TransitPO
                        transit = TransitPO(
                            id=generate_uuid(),
                            from_activity_id=current_act.id,
                            to_activity_id=next_act.id,
                            transport_mode=mode,  # Correct field name
                            trip_day_id=day.id, # Add trip_day_id
                            duration_seconds=int(duration), # Correct field name
                            distance_meters=distance, # Correct field name
                            departure_time=current_act.end_time, # Correct field name
                            arrival_time=(datetime.combine(date.today(), current_act.end_time) + timedelta(minutes=duration_minutes)).time(), # Correct field name
                            cost_amount=0, 
                        )
                        
                        # Check if transit already exists to avoid duplicates (optional, but good for re-running)
                        existing_transit = session.query(TransitPO).filter_by(from_activity_id=current_act.id, to_activity_id=next_act.id).first()
                        if existing_transit:
                            session.delete(existing_transit)
                            
                        session.add(transit)
                        print(f"      Route added: {mode}, {transit.distance_meters/1000:.2f}km, {transit.duration_seconds/60:.0f}min")
                    else:
                        print(f"      Error: Could not find route from {origin.name} to {destination.name}")
                    
                    # Be nice to the API rate limit
                    time.sleep(0.2)
            
            session.commit() # Commit per trip

        print("Route calculation completed successfully!")

    except Exception as e:
        session.rollback()
        print(f"Error calculating routes: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    add_routes()
