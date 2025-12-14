import { useState } from 'react';
import Modal from '../../components/Modal';
import Button from '../../components/Button';
import { updateTransit } from '../../api/travel';
import { toast } from 'react-hot-toast';
import { Car, Footprints, Bus, Bike } from 'lucide-react';
import styles from './ActivityModal.module.css'; // Reusing similar styles

const EditTransitModal = ({ tripId, dayIndex, transit, onClose, onSuccess, isOpen = true }) => {
    const initialMode = typeof transit?.mode === 'string' && transit.mode
        ? transit.mode.toLowerCase()
        : 'walking';
    const [mode, setMode] = useState(initialMode);
    const [loading, setLoading] = useState(false);

    const TRANSIT_OPTIONS = [
        { value: 'walking', label: '步行', icon: Footprints },
        { value: 'driving', label: '驾车', icon: Car },
        { value: 'transit', label: '公共交通', icon: Bus },
        { value: 'cycling', label: '骑行', icon: Bike },
    ];

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);

        try {
            // Only sending the new mode. Backend should handle re-calculation.
            await updateTransit(tripId, dayIndex, transit.id, { transport_mode: mode });
            toast.success('交通方式已更新');
            onSuccess();
            onClose();
        } catch (error) {
            console.error('Failed to update transit', error);
            // Handle backend specific error messages if available
            const msg = error.response?.data?.error || error.response?.data?.detail || '更新失败，请重试';
            toast.error(msg);
        } finally {
            setLoading(false);
        }
    };

    return (
        <Modal title="修改交通方式" onClose={onClose} isOpen={isOpen}>
            <form onSubmit={handleSubmit} className={styles.form}>
                <div className={styles.formGroup}>
                    <label>选择交通方式</label>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem' }}>
                        {TRANSIT_OPTIONS.map((opt) => {
                            const Icon = opt.icon;
                            const isSelected = String(mode).toLowerCase() === opt.value;
                            return (
                                <div
                                    key={opt.value}
                                    onClick={() => setMode(opt.value)}
                                    style={{
                                        padding: '1rem',
                                        border: `2px solid ${isSelected ? 'var(--color-travel)' : 'var(--border-color)'}`,
                                        borderRadius: 'var(--radius-md)',
                                        cursor: 'pointer',
                                        display: 'flex',
                                        flexDirection: 'column',
                                        alignItems: 'center',
                                        gap: '0.5rem',
                                        backgroundColor: isSelected ? 'rgba(249, 115, 22, 0.1)' : 'var(--bg-secondary)',
                                        transition: 'all 0.2s'
                                    }}
                                >
                                    <Icon size={24} color={isSelected ? 'var(--color-travel)' : 'var(--text-secondary)'} />
                                    <span style={{ 
                                        fontWeight: isSelected ? 'bold' : 'normal',
                                        color: isSelected ? 'var(--color-travel)' : 'var(--text-primary)'
                                    }}>
                                        {opt.label}
                                    </span>
                                </div>
                            );
                        })}
                    </div>
                    <p style={{ fontSize: '0.85rem', color: '#64748b', marginTop: '0.5rem' }}>
                        注意：修改交通方式后，系统将重新计算路线、耗时和费用。若选择的方式不可达（如距离过远），系统可能会自动回退或报错。
                    </p>
                </div>

                <div className={styles.actions}>
                    <Button type="button" variant="secondary" onClick={onClose} disabled={loading}>
                        取消
                    </Button>
                    <Button type="submit" variant="travel" disabled={loading}>
                        {loading ? '更新中...' : '确认修改'}
                    </Button>
                </div>
            </form>
        </Modal>
    );
};

export default EditTransitModal;
