import { useState } from 'react';
import { updateTrip, uploadTripCover } from '../../api/travel';
import Button from '../../components/Button';
import Input from '../../components/Input';
import Modal from '../../components/Modal';
import LoadingSpinner from '../../components/LoadingSpinner';
import { toast } from 'react-hot-toast';
import styles from './EditTripModal.module.css';

const EditTripModal = ({ trip, onClose, onSuccess, isOpen = true }) => {
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
            toast.success("更新旅行成功");
            onSuccess();
            onClose();
        } catch (error) {
            console.error("Failed to update trip", error);
            toast.error("更新旅行失败");
        } finally {
            setLoading(false);
        }
    };

    return (
        <Modal
            title="编辑旅行信息"
            isOpen={isOpen}
            onClose={onClose}
        >
            <form onSubmit={handleSubmit} className={styles.form}>
                <Input
                    label="旅行名称"
                    value={formData.name}
                    onChange={e => setFormData({ ...formData, name: e.target.value })}
                    required
                />
                
                <div className={styles.fieldGroup}>
                    <label className={styles.label}>可见性</label>
                    <select
                        value={formData.visibility}
                        onChange={e => setFormData({ ...formData, visibility: e.target.value })}
                        className={styles.select}
                    >
                        <option value="private">私有</option>
                        <option value="public">公开</option>
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

                <div className={styles.fieldGroup}>
                    <label className={styles.label}>封面图片</label>
                    {trip.cover_image_url && !coverFile && (
                        <div className={styles.currentCover}>
                            <img src={trip.cover_image_url} alt="Current Cover" className={styles.coverImage} />
                            <p className={styles.coverText}>当前封面</p>
                        </div>
                    )}
                    <input
                        type="file"
                        accept="image/*"
                        onChange={e => setCoverFile(e.target.files[0])}
                        className={styles.fileInput}
                    />
                </div>

                <div className={styles.actions}>
                    <Button type="button" variant="secondary" onClick={onClose} disabled={loading}>
                        取消
                    </Button>
                    <Button type="submit" variant="travel" disabled={loading}>
                        {loading ? (
                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                <LoadingSpinner size="small" />
                                <span>保存中...</span>
                            </div>
                        ) : '保存更改'}
                    </Button>
                </div>
            </form>
        </Modal>
    );
};

export default EditTripModal;
