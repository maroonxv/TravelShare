import { useState, useEffect } from 'react';
import { getPublicTrips } from '../../api/travel';
import TripCard from '../../components/TripCard';
import styles from './TravelList.module.css';

const PublicTripsPage = () => {
    const [trips, setTrips] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchTrips = async () => {
            try {
                const data = await getPublicTrips();
                setTrips(Array.isArray(data) ? data : (data.trips || []));
            } catch (error) {
                console.error("Failed to fetch public trips", error);
            } finally {
                setLoading(false);
            }
        };
        fetchTrips();
    }, []);

    return (
        <div className={styles.container}>
            <div className={styles.header}>
                <h1 className={styles.title}>Public Trips Gallery</h1>
                <p className={styles.subtitle}>Explore adventures shared by others</p>
            </div>

            {loading ? (
                <div className={styles.loading}>Loading trips...</div>
            ) : (
                <div className={styles.grid}>
                    {trips.length > 0 ? (
                        trips.map(trip => <TripCard key={trip.id} trip={trip} />)
                    ) : (
                        <div className={styles.empty}>No public trips found.</div>
                    )}
                </div>
            )}
        </div>
    );
};

export default PublicTripsPage;
