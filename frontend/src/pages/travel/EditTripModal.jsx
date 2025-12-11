import { useState } from 'react';
import { updateTrip, uploadTripCover } from '../../api/travel';
import Button from '../../components/Button';
import Input from '../../components/Input';
import Card from '../../components/Card';
import { X } from 'lucide-react';
import styles from './TravelList.module.css'; // Reusing styles

const EditTripModal = ({ trip, onClose, onSuccess }) => {
    const [formData, setFormData] = useState({
        name: trip.name,
        description: trip.description || '',
        budget_amount: trip.budget_amount || '',
        visibility: trip.visibility || 'private'
    });
    const [coverFile, setCoverFile] = useState(null);
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            let coverUrl = trip.cover_image_url;
            if (coverFile) {
                const uploadRes = await uploadTripCover(coverFile);
                coverUrl = uploadRes.url;
            }

            const payload = {
                ...formData,
                cover_image_url: coverUrl
            };
            if (!payload.budget_amount) {
                payload.budget_amount = 0;
            }

            await updateTrip(trip.id, payload);
            onSuccess();
            onClose();
        } catch (error) {
            console.error("Failed to update trip", error);
            alert("更新旅行失败");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className={styles.modalOverlay}>
            <Card className={styles.modalContent} title="编辑旅行信息">
                <button className={styles.closeBtn} onClick={onClose}>
                    <X size={20} />
                </button>
                <form onSubmit={handleSubmit} className={styles.form}>
                    <Input
                        label="旅行名称"
                        value={formData.name}
                        onChange={e => setFormData({ ...formData, name: e.target.value })}
                        required
                    />
                    
                    <div style={{ marginBottom: '1rem' }}>
                        <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 500 }}>可见性</label>
                        <select
                            value={formData.visibility}
                            onChange={e => setFormData({ ...formData, visibility: e.target.value })}
                            style={{ width: '100%', padding: '0.75rem', borderRadius: '8px', border: '1px solid #cbd5e1' }}
                        >
                            <option value="private">私有 (Private)</option>
                            <option value="public">公开 (Public)</option>
                            <option value="shared">共享 (Shared)</option>
                        </select>
                    </div>

                    <Input
                        label="预算 (￥)"
                        type="number"
                        value={formData.budget_amount}
                        onChange={e => setFormData({ ...formData, budget_amount: e.target.value })}
                    />
                    
                    <Input
                        label="描述"
                        value={formData.description}
                        onChange={e => setFormData({ ...formData, description: e.target.value })}
                        isTextArea
                    />

                    <div style={{ marginBottom: '1rem' }}>
                        <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 500 }}>封面图片</label>
                        {trip.cover_image_url && !coverFile && (
                            <div style={{ marginBottom: '0.5rem' }}>
                                <img src={trip.cover_image_url} alt="Current Cover" style={{ width: '100px', height: '60px', objectFit: 'cover', borderRadius: '4px' }} />
                                <p style={{ fontSize: '0.8rem', color: '#64748b' }}>当前封面</p>
                            </div>
                        )}
                        <input
                            type="file"
                            accept="image/*"
                            onChange={e => setCoverFile(e.target.files[0])}
                            style={{ width: '100%' }}
                        />
                    </div>

                    <div style={{ display: 'flex', gap: '1rem', justifyContent: 'flex-end', marginTop: '1rem' }}>
                        <Button type="button" variant="secondary" onClick={onClose} disabled={loading}>
                            取消
                        </Button>
                        <Button type="submit" variant="travel" disabled={loading}>
                            {loading ? '保存中...' : '保存更改'}
                        </Button>
                    </div>
                </form>
            </Card>
        </div>
    );
};

export default EditTripModal;
