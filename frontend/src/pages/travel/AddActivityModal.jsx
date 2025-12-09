import { useState } from 'react';
import { addActivity } from '../../api/travel';
import Button from '../../components/Button';
import Input from '../../components/Input';
import Card from '../../components/Card';
import { X } from 'lucide-react';
import styles from './TripDetail.module.css'; // Share styles

const AddActivityModal = ({ tripId, dayIndex, onClose, onSuccess }) => {
    const [formData, setFormData] = useState({
        name: '',
        activity_type: 'sightseeing', // Default
        location_name: '',
        start_time: '',
        end_time: '',
        cost: 0,
        currency: 'USD'
    });
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            await addActivity(tripId, dayIndex, formData);
            onSuccess();
            onClose();
        } catch (error) {
            console.error("Failed to add activity", error);
            alert("Failed to add activity");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className={styles.modalOverlay}>
            <Card className={styles.modalContent} title="Add Activity">
                <button className={styles.closeBtn} onClick={onClose}>
                    <X size={20} />
                </button>
                <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                    <Input
                        label="Activity Name"
                        value={formData.name}
                        onChange={e => setFormData({ ...formData, name: e.target.value })}
                        required
                    />
                    <div style={{ display: 'flex', gap: '1rem' }}>
                        <Input
                            label="Type"
                            value={formData.activity_type}
                            onChange={e => setFormData({ ...formData, activity_type: e.target.value })}
                            required
                        />
                        <Input
                            label="Location"
                            value={formData.location_name}
                            onChange={e => setFormData({ ...formData, location_name: e.target.value })}
                            required
                        />
                    </div>
                    <div style={{ display: 'flex', gap: '1rem' }}>
                        <Input
                            label="Start Time"
                            type="time"
                            value={formData.start_time}
                            onChange={e => setFormData({ ...formData, start_time: e.target.value })}
                            required
                        />
                        <Input
                            label="End Time"
                            type="time"
                            value={formData.end_time}
                            onChange={e => setFormData({ ...formData, end_time: e.target.value })}
                            required
                        />
                    </div>
                    <Input
                        label="Cost"
                        type="number"
                        value={formData.cost}
                        onChange={e => setFormData({ ...formData, cost: e.target.value })}
                    />

                    <Button type="submit" variant="travel" disabled={loading}>
                        {loading ? 'Adding...' : 'Add Activity'}
                    </Button>
                </form>
            </Card>
        </div>
    );
};

export default AddActivityModal;
