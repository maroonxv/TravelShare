import { useState, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { Search, Send, X } from 'lucide-react';
import styles from './ShareModal.module.css';
import { getConversations, sendMessage } from '../../api/social';
import Input from '../../components/Input';
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
            // Prevent body scroll when modal is open
            document.body.style.overflow = 'hidden';
        } else {
            document.body.style.overflow = 'unset';
        }
        return () => {
            document.body.style.overflow = 'unset';
        };
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
                content: comment || '分享了一个帖子',
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

    if (!isOpen) return null;

    const filteredConversations = conversations.filter(c => 
        c.name.toLowerCase().includes(search.toLowerCase())
    );

    return createPortal(
        <div className={styles.overlay} onClick={onClose}>
            <div className={styles.modal} onClick={e => e.stopPropagation()}>
                <div className={styles.header}>
                    <h3>分享帖子</h3>
                    <button className={styles.closeButton} onClick={onClose}>
                        <X size={20} />
                    </button>
                </div>

                <div className={styles.content}>
                    <div className={styles.searchBar}>
                        <Search className={styles.searchIcon} size={18} />
                        <input 
                            type="text"
                            placeholder="搜索会话..." 
                            value={search}
                            onChange={e => setSearch(e.target.value)}
                            className={styles.searchInput}
                        />
                    </div>

                    <div className={styles.list}>
                        {loading ? (
                            <div className={styles.loading}>
                                <LoadingSpinner size="small" />
                                <span>加载会话中...</span>
                            </div>
                        ) : filteredConversations.length === 0 ? (
                            <div className={styles.empty}>未找到相关会话</div>
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
                                    <div className={styles.info}>
                                        <div className={styles.name}>{conv.name}</div>
                                        <div className={styles.subtext}>点击选择</div>
                                    </div>
                                    {selectedConvId === conv.id && <div className={styles.indicator} />}
                                </div>
                            ))
                        )}
                    </div>
                    
                    <div className={styles.commentSection}>
                        <input 
                            placeholder="添加留言 (可选)..." 
                            value={comment}
                            onChange={e => setComment(e.target.value)}
                            className={styles.commentInput}
                        />
                    </div>
                </div>

                <div className={styles.footer}>
                    <button className={styles.cancelButton} onClick={onClose}>取消</button>
                    <button 
                        className={styles.sendButton} 
                        onClick={handleSend}
                        disabled={!selectedConvId || sending}
                    >
                        {sending ? '发送中...' : (
                            <>
                                <span>发送</span>
                                <Send size={16} />
                            </>
                        )}
                    </button>
                </div>
            </div>
        </div>,
        document.body
    );
};

export default ShareModal;
