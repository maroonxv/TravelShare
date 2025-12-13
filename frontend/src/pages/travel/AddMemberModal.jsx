import { useState, useEffect } from 'react';
import { addMember } from '../../api/travel';
import { getFriends } from '../../api/social';
import Button from '../../components/Button';
import Modal from '../../components/Modal';
import LoadingSpinner from '../../components/LoadingSpinner';
import { toast } from 'react-hot-toast';
import styles from './AddMemberModal.module.css';

const AddMemberModal = ({ tripId, onClose, onSuccess, isOpen = true }) => {
    const [userId, setUserId] = useState('');
    const [loading, setLoading] = useState(false);
    const [friends, setFriends] = useState([]);
    const [loadingFriends, setLoadingFriends] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        const loadFriends = async () => {
            try {
                const data = await getFriends();
                setFriends(data || []);
            } catch (err) {
                console.error("Failed to load friends", err);
                toast.error("无法加载好友列表");
            } finally {
                setLoadingFriends(false);
            }
        };
        loadFriends();
    }, []);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!userId) {
            toast.error("请选择一个好友");
            return;
        }
        setLoading(true);
        setError('');
        
        try {
            await addMember(tripId, userId);
            toast.success("添加成员成功");
            onSuccess();
            onClose();
        } catch (err) {
            console.error("Failed to add member", err);
            const errMsg = err.response?.data?.error || "添加成员失败";
            toast.error(errMsg);
            setError(errMsg);
        } finally {
            setLoading(false);
        }
    };

    return (
        <Modal
            title="添加成员"
            isOpen={isOpen}
            onClose={onClose}
        >
            <form onSubmit={handleSubmit} className={styles.form}>
                <div className={styles.infoText}>
                    <small>
                        请从您的好友列表中选择成员。
                    </small>
                </div>
                
                {loadingFriends ? (
                    <div className={styles.emptyState}>
                        <LoadingSpinner size="medium" />
                    </div>
                ) : friends.length === 0 ? (
                    <div className={styles.emptyState}>
                        暂无好友可添加
                    </div>
                ) : (
                    <select
                        value={userId}
                        onChange={e => setUserId(e.target.value)}
                        className={styles.select}
                        required
                    >
                        <option value="">-- 选择好友 --</option>
                        {friends.map(friend => (
                            <option key={friend.id} value={friend.id}>
                                {friend.username} ({friend.nickname || '无昵称'})
                            </option>
                        ))}
                    </select>
                )}
                
                {error && <div className={styles.error}>{error}</div>}

                <div className={styles.actions}>
                    <Button type="button" variant="secondary" onClick={onClose}>
                        取消
                    </Button>
                    <Button type="submit" variant="travel" disabled={loading || !userId}>
                        {loading ? (
                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                <LoadingSpinner size="small" />
                                <span>添加中...</span>
                            </div>
                        ) : '添加成员'}
                    </Button>
                </div>
            </form>
        </Modal>
    );
};

export default AddMemberModal;
