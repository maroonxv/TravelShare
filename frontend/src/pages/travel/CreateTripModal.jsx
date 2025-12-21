import { useState } from 'react';
import { createTrip, uploadTripCover } from '../../api/travel';
import { useAuth } from '../../context/useAuth';
import Button from '../../components/Button';
import Input from '../../components/Input';
import Modal from '../../components/Modal';
import LoadingSpinner from '../../components/LoadingSpinner';
import { toast } from 'react-hot-toast';
import styles from './CreateTripModal.module.css';

const CreateTripModal = ({ onClose, onSuccess, isOpen = true }) => {
    const { user } = useAuth();
    const [newTrip, setNewTrip] = useState({
        name: '',
        start_date: '',
        end_date: '',
        budget_amount: '',
        description: '',
        visibility: 'private'
    });
    const [coverFile, setCoverFile] = useState(null);
    const [loading, setLoading] = useState(false);

    const handleCreate = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            let coverUrl = null;
            if (coverFile) {
                const uploadRes = await uploadTripCover(coverFile);
                coverUrl = uploadRes.url;
            }

            const payload = { 
                ...newTrip, 
                creator_id: user.id,
                cover_image_url: coverUrl
            };
            if (!payload.budget_amount) {
                delete payload.budget_amount;
            }
            await createTrip(payload);
            toast.success("创建旅行成功");
            onSuccess();
            onClose();
        } catch (error) {
            console.error("Failed to create trip", error);
            const errMsg = error.response?.data?.error || error.message || "Unknown error";
            toast.error(`创建旅行失败: ${errMsg}`);
        } finally {
            setLoading(false);
        }
    };

    return (
        <Modal
            title="计划一次新旅行"
            isOpen={isOpen}
            onClose={onClose}
        >
            <form onSubmit={handleCreate} className={styles.form}>
                <Input
                    label="旅行名称"
                    value={newTrip.name}
                    onChange={e => setNewTrip({ ...newTrip, name: e.target.value })}
                    required
                />
                <div className={styles.row}>
                    <Input
                        label="开始日期"
                        type="date"
                        value={newTrip.start_date}
                        onChange={e => setNewTrip({ ...newTrip, start_date: e.target.value })}
                        required
                    />
                    <Input
                        label="结束日期"
                        type="date"
                        value={newTrip.end_date}
                        onChange={e => setNewTrip({ ...newTrip, end_date: e.target.value })}
                        required
                    />
                </div>
                <Input
                    label="预算 (￥)"
                    type="number"
                    value={newTrip.budget_amount}
                    onChange={e => setNewTrip({ ...newTrip, budget_amount: e.target.value })}
                />
                <Input
                    label="描述"
                    value={newTrip.description}
                    onChange={e => setNewTrip({ ...newTrip, description: e.target.value })}
                />
                
                <div className={styles.fieldGroup}>
                    <label className={styles.label}>可见性</label>
                    <select
                        value={newTrip.visibility}
                        onChange={e => setNewTrip({ ...newTrip, visibility: e.target.value })}
                        className={styles.select}
                    >
                        <option value="private">私有</option>
                        <option value="public">公开</option>
                    </select>
                </div>

                <div className={styles.fieldGroup}>
                    <label className={styles.label}>封面图片</label>
                    <input
                        type="file"
                        accept="image/*"
                        onChange={e => setCoverFile(e.target.files[0])}
                        className={styles.fileInput}
                    />
                </div>

                <div className={styles.actions}>
                    <Button type="button" variant="secondary" onClick={onClose}>
                        取消
                    </Button>
                    <Button type="submit" variant="travel" disabled={loading}>
                        {loading ? (
                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                <LoadingSpinner size="small" />
                                <span>创建中...</span>
                            </div>
                        ) : '创建旅行'}
                    </Button>
                </div>
            </form>
        </Modal>
    );
};

export default CreateTripModal;
