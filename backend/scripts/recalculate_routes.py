import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from shared.database.core import SessionLocal
from app_travel.infrastructure.database.dao_impl.sqlalchemy_trip_dao import SqlAlchemyTripDao
from app_travel.infrastructure.database.repository_impl.trip_repository_impl import TripRepositoryImpl
from app_travel.infrastructure.external_service.gaode_geo_service_impl import GaodeGeoServiceImpl
from app_travel.domain.domain_service.itinerary_service import ItineraryService
from app_travel.domain.aggregate.trip_aggregate import Trip
from sqlalchemy import select
from app_travel.infrastructure.database.persistent_model.trip_po import TripPO

def recalculate_routes():
    session = SessionLocal()
    try:
        print("Starting route recalculation...")
        
        # Initialize services
        trip_dao = SqlAlchemyTripDao(session)
        trip_repo = TripRepositoryImpl(trip_dao)
        geo_service = GaodeGeoServiceImpl()
        itinerary_service = ItineraryService(geo_service)
        
        # Get all trips
        # Note: Ideally fetch in batches if database is huge
        stmt = select(TripPO)
        trip_pos = session.execute(stmt).scalars().all()
        
        print(f"Found {len(trip_pos)} trips to process.")
        
        for trip_po in trip_pos:
            trip = trip_repo.find_by_id(trip_po.to_domain().id)
            if not trip:
                continue
                
            print(f"Processing Trip: {trip.name.value} ({trip.id.value})")
            
            updated = False
            for day in trip.days:
                activities = day.activities
                if len(activities) < 2:
                    continue
                    
                # Clear existing transits for recalculation
                # Note: We keep the user's preferred mode if we had that logic, 
                # but for this script we might just recalculate everything using smart fallback
                # or try to preserve mode if transit exists.
                
                # However, the user asked to recalculate because some are missing.
                # A safe approach is to clear and recalculate all transits for the day.
                
                # Backup existing modes if any
                preferred_modes = {}
                for t in day.transits:
                    preferred_modes[(t.from_activity_id, t.to_activity_id)] = t.transport_mode

                # Recalculate
                print(f"  Day {day.day_number}: Recalculating {len(activities)} activities...")
                try:
                    result = itinerary_service.calculate_transits_between_activities(
                        activities, 
                        preferred_modes=preferred_modes
                    )
                    
                    # Update day transits
                    # Since calculate_transits_between_activities returns a new list of transits
                    # we should replace the old ones.
                    # But we need to be careful with IDs if we want to preserve them? 
                    # The domain logic usually generates new IDs for new transit objects.
                    # Let's just replace them.
                    
                    day._transits = result.transits
                    updated = True
                    print(f"  Day {day.day_number}: Updated {len(result.transits)} transits.")
                    
                    if result.warnings:
                        for w in result.warnings:
                            print(f"    [Warning] {w.message}")
                            
                except Exception as e:
                    print(f"  Day {day.day_number}: Error recalculating - {e}")
            
            if updated:
                trip_repo.save(trip)
                print(f"Trip {trip.id.value} saved.")
                
        session.commit()
        print("Recalculation completed successfully.")
        
    except Exception as e:
        session.rollback()
        print(f"Script failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    recalculate_routes()
