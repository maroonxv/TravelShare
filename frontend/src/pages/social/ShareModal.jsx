import { useState, useEffect } from 'react';
import { Search } from 'lucide-react';
import styles from './ShareModal.module.css';
import { getConversations, sendMessage } from '../../api/social';
import Input from '../../components/Input';
import Modal from '../../components/Modal';
import LoadingSpinner from '../../components/LoadingSpinner';
import toast from 'react-hot-toast';

const ShareModal = ({ isOpen, onClose, post }) => {
    const [conversations, setConversations] = useState([]);
    const [selectedConvId, setSelectedConvId] = useState(null);
    const [comment, setComment] = useState('');
    const [search, setSearch] = useState('');
    const [loading, setLoading] = useState(false);
    const [sending, setSending] = useState(false);

    useEffect(() => {
        if (isOpen) {
            loadConversations();
        }
    }, [isOpen]);

    const loadConversations = async () => {
        setLoading(true);
        try {
            const data = await getConversations();
            setConversations(data);
        } catch (error) {
            console.error("Failed to load conversations", error);
            toast.error("加载会话列表失败");
        } finally {
            setLoading(false);
        }
    };

    const handleSend = async () => {
        if (!selectedConvId) return;
        setSending(true);
        try {
            await sendMessage(selectedConvId, {
                content: comment || 'Shared a post',
                type: 'share_post',
                reference_id: post.id
            });
            onClose();
            toast.success("分享成功！");
        } catch (error) {
            console.error("Failed to share post", error);
            toast.error("分享失败");
        } finally {
            setSending(false);
        }
    };

    const filteredConversations = conversations.filter(c => 
        c.name.toLowerCase().includes(search.toLowerCase())
    );

    return (
        <Modal title="分享帖子" isOpen={isOpen} onClose={onClose}>
            <div className={styles.content}>
                <div className={styles.searchBar}>
                    <Input 
                        placeholder="搜索会话..." 
                        value={search}
                        onChange={e => setSearch(e.target.value)}
                        icon={Search}
                    />
                </div>

                <div className={styles.list}>
                    {loading ? (
                        <div className={styles.loading}><LoadingSpinner size="small" /> 加载中...</div>
                    ) : filteredConversations.length === 0 ? (
                        <div className={styles.empty}>没有找到会话</div>
                    ) : (
                        filteredConversations.map(conv => (
                            <div 
                                key={conv.id} 
                                className={`${styles.item} ${selectedConvId === conv.id ? styles.selected : ''}`}
                                onClick={() => setSelectedConvId(conv.id)}
                            >
                                <div className={styles.avatar}>
                                    {conv.other_user_avatar ? (
                                        <img src={conv.other_user_avatar} alt={conv.name} />
                                    ) : (
                                        conv.name.charAt(0).toUpperCase()
                                    )}
                                </div>
                                <div className={styles.name}>{conv.name}</div>
                            </div>
                        ))
                    )}
                </div>
                
                {selectedConvId && (
                    <div className={styles.commentInput}>
                        <Input 
                            placeholder="留言..." 
                            value={comment}
                            onChange={e => setComment(e.target.value)}
                        />
                    </div>
                )}
            </div>

            <div className={styles.footer}>
                <button className={styles.cancelButton} onClick={onClose}>取消</button>
                <button 
                    className={styles.sendButton} 
                    onClick={handleSend}
                    disabled={!selectedConvId || sending}
                >
                    {sending ? '发送中...' : '发送'}
                </button>
            </div>
        </Modal>
    );
};

export default ShareModal;
