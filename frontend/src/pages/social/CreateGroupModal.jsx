import { useState, useEffect } from 'react';
import { Users, X, User, Check } from 'lucide-react';
import { getFriends, createGroupChat } from '../../api/social';
import Button from '../../components/Button';
import Input from '../../components/Input';
import styles from './CreateGroupModal.module.css';

const CreateGroupModal = ({ onClose, onSuccess }) => {
    const [title, setTitle] = useState('');
    const [friends, setFriends] = useState([]);
    const [selectedFriends, setSelectedFriends] = useState(new Set());
    const [loading, setLoading] = useState(false);
    const [submitting, setSubmitting] = useState(false);

    useEffect(() => {
        loadFriends();
    }, []);

    const loadFriends = async () => {
        setLoading(true);
        try {
            const data = await getFriends();
            setFriends(Array.isArray(data) ? data : []);
        } catch (error) {
            console.error("Failed to load friends", error);
        } finally {
            setLoading(false);
        }
    };

    const toggleFriend = (friendId) => {
        setSelectedFriends(prev => {
            const next = new Set(prev);
            if (next.has(friendId)) {
                next.delete(friendId);
            } else {
                next.add(friendId);
            }
            return next;
        });
    };

    const handleCreate = async () => {
        if (!title.trim()) {
            alert("请输入群组名称");
            return;
        }
        if (selectedFriends.size === 0) {
            alert("请至少选择一位好友");
            return;
        }

        setSubmitting(true);
        try {
            await createGroupChat(title, Array.from(selectedFriends));
            onSuccess();
            onClose();
        } catch (error) {
            console.error("Failed to create group", error);
            alert("创建群组失败: " + (error.response?.data?.error || error.message));
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <div className={styles.overlay} onClick={onClose}>
            <div className={styles.modal} onClick={e => e.stopPropagation()}>
                <div className={styles.header}>
                    <h3>创建群聊</h3>
                    <button className={styles.closeBtn} onClick={onClose}><X size={20}/></button>
                </div>
                
                <div className={styles.body}>
                    <div className={styles.field}>
                        <label>群组名称</label>
                        <Input 
                            placeholder="输入群组名称..." 
                            value={title}
                            onChange={e => setTitle(e.target.value)}
                            autoFocus
                        />
                    </div>

                    <div className={styles.field}>
                        <label>选择成员 ({selectedFriends.size})</label>
                        <div className={styles.friendList}>
                            {loading && <div className={styles.loading}>加载好友中...</div>}
                            {!loading && friends.length === 0 && (
                                <div className={styles.empty}>暂无好友</div>
                            )}
                            {friends.map(friend => (
                                <div 
                                    key={friend.id} 
                                    className={`${styles.friendRow} ${selectedFriends.has(friend.id) ? styles.selected : ''}`}
                                    onClick={() => toggleFriend(friend.id)}
                                >
                                    <div className={styles.userInfo}>
                                        {friend.avatar ? (
                                            <img src={friend.avatar} className={styles.avatar} alt="" />
                                        ) : (
                                            <div className={styles.avatarPlaceholder}><User size={20}/></div>
                                        )}
                                        <span className={styles.username}>{friend.name}</span>
                                    </div>
                                    {selectedFriends.has(friend.id) && (
                                        <Check size={18} className={styles.checkIcon} />
                                    )}
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                <div className={styles.footer}>
                    <Button variant="secondary" onClick={onClose}>取消</Button>
                    <Button 
                        variant="primary" 
                        onClick={handleCreate} 
                        disabled={submitting || !title.trim() || selectedFriends.size === 0}
                    >
                        {submitting ? '创建中...' : '创建'}
                    </Button>
                </div>
            </div>
        </div>
    );
};

export default CreateGroupModal;
