import { useState, useEffect } from 'react';
import { addMember } from '../../api/travel';
import { getFriends } from '../../api/social';
import Button from '../../components/Button';
import Card from '../../components/Card';
import { X } from 'lucide-react';
import styles from './TripDetail.module.css';

const AddMemberModal = ({ tripId, onClose, onSuccess }) => {
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
                setError("无法加载好友列表");
            } finally {
                setLoadingFriends(false);
            }
        };
        loadFriends();
    }, []);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!userId) {
            setError("请选择一个好友");
            return;
        }
        setLoading(true);
        setError('');
        
        try {
            await addMember(tripId, userId);
            onSuccess();
            onClose();
        } catch (err) {
            console.error("Failed to add member", err);
            const errMsg = err.response?.data?.error || "添加成员失败";
            setError(errMsg);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className={styles.modalOverlay}>
            <Card className={styles.modalContent} title="添加成员">
                <button className={styles.closeBtn} onClick={onClose}>
                    <X size={20} />
                </button>
                <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                    <div className={styles.infoText}>
                        <small style={{ color: '#64748b', marginBottom: '0.5rem', display: 'block' }}>
                            请从您的好友列表中选择成员。
                        </small>
                    </div>
                    
                    {loadingFriends ? (
                        <div>加载好友中...</div>
                    ) : friends.length === 0 ? (
                        <div style={{ padding: '1rem', textAlign: 'center', color: '#64748b' }}>
                            暂无好友可添加
                        </div>
                    ) : (
                        <select
                            value={userId}
                            onChange={e => setUserId(e.target.value)}
                            style={{
                                padding: '0.5rem',
                                borderRadius: '0.25rem',
                                border: '1px solid #cbd5e1',
                                width: '100%',
                                fontSize: '1rem'
                            }}
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
                    
                    {error && <div className={styles.error} style={{color: 'red', fontSize: '0.9rem'}}>{error}</div>}

                    <div style={{ display: 'flex', gap: '1rem', justifyContent: 'flex-end', marginTop: '1rem' }}>
                        <Button type="button" variant="secondary" onClick={onClose}>
                            取消
                        </Button>
                        <Button type="submit" variant="travel" disabled={loading || !userId}>
                            {loading ? '添加中...' : '添加成员'}
                        </Button>
                    </div>
                </form>
            </Card>
        </div>
    );
};

export default AddMemberModal;
