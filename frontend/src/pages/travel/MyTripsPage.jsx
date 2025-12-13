import { useState, useEffect } from 'react';
import { getUserTrips } from '../../api/travel';
import { useAuth } from '../../context/AuthContext';
import TripCard from '../../components/TripCard';
import Button from '../../components/Button';
import LoadingSpinner from '../../components/LoadingSpinner';
import CreateTripModal from './CreateTripModal';
import { Plus } from 'lucide-react';
import styles from './TravelList.module.css';

const MyTripsPage = () => {
    const { user } = useAuth();
    const [trips, setTrips] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showModal, setShowModal] = useState(false);

    useEffect(() => {
        if (user) loadTrips();
    }, [user]);

    const loadTrips = async () => {
        try {
            const data = await getUserTrips(user.id);
            setTrips(Array.isArray(data) ? data : (data.trips || []));
        } catch (error) {
            console.error("Failed to load trips", error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div>
            <div style={{ marginBottom: '1.5rem', display: 'flex', justifyContent: 'flex-end' }}>
                <Button variant="travel" onClick={() => setShowModal(true)}>
                    <Plus size={20} style={{ marginRight: '0.5rem' }} />
                    新建旅行
                </Button>
            </div>

            {loading ? (
                <div className={styles.loading}>
                    <LoadingSpinner size="large" />
                </div>
            ) : (
                <div className={styles.grid}>
                    {trips.length > 0 ? (
                        trips.map(trip => <TripCard key={trip.id} trip={trip} />)
                    ) : (
                        <div className={styles.empty}>你还没有创建任何旅行计划。</div>
                    )}
                </div>
            )}

            {showModal && (
                <CreateTripModal
                    isOpen={showModal}
                    onClose={() => setShowModal(false)}
                    onSuccess={loadTrips}
                />
            )}
        </div>
    );
};

export default MyTripsPage;
