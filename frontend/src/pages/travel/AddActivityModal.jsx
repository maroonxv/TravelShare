import { useState } from 'react';
import { addActivity } from '../../api/travel';
import Button from '../../components/Button';
import Input from '../../components/Input';
import Modal from '../../components/Modal';
import LoadingSpinner from '../../components/LoadingSpinner';
import { toast } from 'react-hot-toast';
import styles from './ActivityModal.module.css';

const AddActivityModal = ({ tripId, dayIndex, onClose, onSuccess, isOpen = true }) => {
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
            // Backend expects cost_amount, not cost
            const payload = {
                ...formData,
                cost_amount: formData.cost,
                cost: undefined
            };
            await addActivity(tripId, dayIndex, payload);
            toast.success("添加活动成功");
            onSuccess();
            onClose();
        } catch (error) {
            console.error("Failed to add activity", error);
            toast.error("添加活动失败");
        } finally {
            setLoading(false);
        }
    };

    return (
        <Modal
            title="添加活动"
            isOpen={isOpen}
            onClose={onClose}
        >
            <form onSubmit={handleSubmit} className={styles.form}>
                <Input
                    label="活动名称"
                    value={formData.name}
                    onChange={e => setFormData({ ...formData, name: e.target.value })}
                    required
                />
                <div className={styles.row}>
                    <Input
                        label="类型"
                        value={formData.activity_type}
                        onChange={e => setFormData({ ...formData, activity_type: e.target.value })}
                        required
                    />
                    <Input
                        label="地点"
                        value={formData.location_name}
                        onChange={e => setFormData({ ...formData, location_name: e.target.value })}
                        required
                    />
                </div>
                <div className={styles.row}>
                    <Input
                        label="开始时间"
                        type="time"
                        value={formData.start_time}
                        onChange={e => setFormData({ ...formData, start_time: e.target.value })}
                        required
                    />
                    <Input
                        label="结束时间"
                        type="time"
                        value={formData.end_time}
                        onChange={e => setFormData({ ...formData, end_time: e.target.value })}
                        required
                    />
                </div>
                <Input
                    label="花费"
                    type="number"
                    value={formData.cost}
                    onChange={e => setFormData({ ...formData, cost: e.target.value })}
                />

                <div className={styles.actions}>
                    <Button type="button" variant="secondary" onClick={onClose}>
                        取消
                    </Button>
                    <Button type="submit" variant="travel" disabled={loading}>
                        {loading ? (
                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                <LoadingSpinner size="small" />
                                <span>添加中...</span>
                            </div>
                        ) : '添加活动'}
                    </Button>
                </div>
            </form>
        </Modal>
    );
};

export default AddActivityModal;
