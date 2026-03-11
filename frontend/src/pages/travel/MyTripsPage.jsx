import { useCallback, useEffect, useState } from 'react';
import { Plus } from 'lucide-react';
import { getUserTrips } from '../../api/travel';
import { useAuth } from '../../context/useAuth';
import TripCard from '../../components/TripCard';
import Button from '../../components/Button';
import LoadingSpinner from '../../components/LoadingSpinner';
import CreateTripModal from './CreateTripModal';
import styles from './TravelList.module.css';

const MyTripsPage = () => {
    const { user } = useAuth();
    const [trips, setTrips] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showModal, setShowModal] = useState(false);

    const loadTrips = useCallback(async () => {
        if (!user?.id) return;
        try {
            const data = await getUserTrips(user.id);
            setTrips(Array.isArray(data) ? data : data.trips || []);
        } catch (error) {
            console.error('Failed to load trips', error);
        } finally {
            setLoading(false);
        }
    }, [user?.id]);

    useEffect(() => {
        if (user) loadTrips();
    }, [loadTrips, user]);

    return (
        <div>
            <div style={{ marginBottom: '1rem', display: 'flex', justifyContent: 'flex-end' }}>
                <Button icon={<Plus size={16} />} variant="travel" onClick={() => setShowModal(true)}>
                    新建行程
                </Button>
            </div>

            {loading ? (
                <div className={styles.loading}>
                    <LoadingSpinner size="large" />
                </div>
            ) : (
                <div className={styles.grid}>
                    {trips.length > 0 ? (
                        trips.map((trip) => <TripCard key={trip.id} trip={trip} />)
                    ) : (
                        <div className={styles.empty}>你还没有创建任何行程计划。</div>
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
