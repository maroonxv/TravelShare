import { useState, useEffect } from 'react';
import { Search, UserPlus, Check, User } from 'lucide-react';
import { searchUsers, sendFriendRequest } from '../../api/social';
import Input from '../../components/Input';
import Modal from '../../components/Modal';
import LoadingSpinner from '../../components/LoadingSpinner';
import toast from 'react-hot-toast';
import styles from './AddFriendModal.module.css';

const AddFriendModal = ({ onClose }) => {
    const [query, setQuery] = useState('');
    const [results, setResults] = useState([]);
    const [loading, setLoading] = useState(false);
    const [sentRequests, setSentRequests] = useState(new Set());

    useEffect(() => {
        const timer = setTimeout(() => {
            if (query.trim()) {
                performSearch();
            } else {
                setResults([]);
            }
        }, 500);
        return () => clearTimeout(timer);
    }, [query]);

    const performSearch = async () => {
        setLoading(true);
        try {
            const data = await searchUsers(query);
            setResults(Array.isArray(data) ? data : []);
        } catch (error) {
            console.error("Search failed", error);
            toast.error("搜索失败");
        } finally {
            setLoading(false);
        }
    };

    const handleAdd = async (userId) => {
        try {
            await sendFriendRequest(userId);
            setSentRequests(prev => new Set(prev).add(userId));
            toast.success("好友请求已发送");
        } catch (error) {
            toast.error("发送请求失败: " + (error.response?.data?.error || error.message));
        }
    };

    return (
        <Modal title="添加好友" isOpen={true} onClose={onClose}>
            <div className={styles.searchBar}>
                <Search size={18} className={styles.searchIcon} />
                <Input 
                    placeholder="搜索用户名..." 
                    value={query}
                    onChange={e => setQuery(e.target.value)}
                    autoFocus
                />
            </div>

            <div className={styles.results}>
                {loading && <div className={styles.loading}><LoadingSpinner size="small" /> 搜索中...</div>}
                {!loading && results.length === 0 && query && (
                    <div className={styles.empty}>未找到用户</div>
                )}
                {results.map(user => (
                    <div key={user.id} className={styles.userRow}>
                        <div className={styles.userInfo}>
                            {user.profile?.avatar_url ? (
                                <img src={user.profile.avatar_url} className={styles.avatar} alt="" />
                            ) : (
                                <div className={styles.avatarPlaceholder}><User size={20}/></div>
                            )}
                            <span className={styles.username}>{user.username}</span>
                        </div>
                        {sentRequests.has(user.id) ? (
                            <span className={styles.sentBadge}><Check size={14} /> 已发送</span>
                        ) : (
                            <button className={styles.addBtn} onClick={() => handleAdd(user.id)}>
                                <UserPlus size={18} />
                            </button>
                        )}
                    </div>
                ))}
            </div>
        </Modal>
    );
};

export default AddFriendModal;
