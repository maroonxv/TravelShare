import { useState, useEffect, useRef, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { io } from 'socket.io-client';
import EmojiPicker from 'emoji-picker-react';
import { 
    getConversations, 
    getMessages, 
    sendMessage, 
    getFriendRequests, 
    acceptFriendRequest, 
    rejectFriendRequest,
    getFriends,
    createConversation,
    getUserProfile,
    addGroupParticipant,
    removeGroupParticipant
} from '../../api/social';
import { useAuth } from '../../context/useAuth';
import { Send, User, Check, X, MessageSquare, ArrowLeft, Smile, Plus, Users, UserPlus, Image as ImageIcon } from 'lucide-react';
import AddFriendModal from './AddFriendModal';
import CreateGroupModal from './CreateGroupModal';
import LoadingSpinner from '../../components/LoadingSpinner';
import Modal from '../../components/Modal';
import toast from 'react-hot-toast';
import styles from './ChatPage.module.css';

const ChatPage = () => {
    const { user } = useAuth();
    const [conversations, setConversations] = useState([]);
    const [requests, setRequests] = useState([]);
    const [friends, setFriends] = useState([]);
    const [activeConvId, setActiveConvId] = useState(null);
    const [messages, setMessages] = useState([]);
    const [newMessage, setNewMessage] = useState('');
    const [loading, setLoading] = useState(true);
    const [showAddFriend, setShowAddFriend] = useState(false);
    const [showCreateGroup, setShowCreateGroup] = useState(false);
    const [showDropdown, setShowDropdown] = useState(false);
    const [showEmojiPicker, setShowEmojiPicker] = useState(false);
    const [selectedFile, setSelectedFile] = useState(null);
    const [showGroupMembers, setShowGroupMembers] = useState(false);
    const [memberProfiles, setMemberProfiles] = useState({});
    const [membersLoading, setMembersLoading] = useState(false);
    const [inviteUserId, setInviteUserId] = useState('');
    const [inviteSubmitting, setInviteSubmitting] = useState(false);
    const [removingUserId, setRemovingUserId] = useState(null);
    
    const messagesEndRef = useRef(null);
    const dropdownRef = useRef(null);
    const socketRef = useRef(null);
    const activeConvIdRef = useRef(activeConvId);
    const conversationsRef = useRef(conversations);
    const memberProfilesRef = useRef(memberProfiles);
    const profileLoadInFlightRef = useRef(new Set());
    const fileInputRef = useRef(null);
    const emojiPickerRef = useRef(null);

    useEffect(() => {
        activeConvIdRef.current = activeConvId;
    }, [activeConvId]);

    useEffect(() => {
        conversationsRef.current = conversations;
    }, [conversations]);

    useEffect(() => {
        memberProfilesRef.current = memberProfiles;
    }, [memberProfiles]);

    const ensureUserProfileLoaded = useCallback(async (userId) => {
        if (!userId) return;
        if (memberProfilesRef.current[userId]) return;
        if (profileLoadInFlightRef.current.has(userId)) return;

        profileLoadInFlightRef.current.add(userId);
        try {
            const profile = await getUserProfile(userId);
            setMemberProfiles(prev => {
                if (prev[userId]) return prev;
                return { ...prev, [userId]: profile };
            });
        } catch {
            setMemberProfiles(prev => {
                if (prev[userId]) return prev;
                return {
                    ...prev,
                    [userId]: { id: userId, username: userId.slice(0, 6), profile: { avatar_url: null } }
                };
            });
        } finally {
            profileLoadInFlightRef.current.delete(userId);
        }
    }, []);

    const loadAllData = useCallback(async () => {
        setLoading(true);
        try {
            const [reqsData, convsData, friendsData] = await Promise.all([
                getFriendRequests(),
                getConversations(),
                getFriends()
            ]);

            setRequests(Array.isArray(reqsData) ? reqsData : []);
            setConversations(Array.isArray(convsData) ? convsData : []);
            setFriends(Array.isArray(friendsData) ? friendsData : []);

            if (window.innerWidth > 900 && Array.isArray(convsData) && convsData.length > 0 && !activeConvIdRef.current) {
                setActiveConvId(convsData[0].id);
            }
        } catch (error) {
            console.error("Failed to load data", error);
            toast.error("加载数据失败");
        } finally {
            setLoading(false);
        }
    }, []);

    const loadMessages = useCallback(async (id) => {
        try {
            const data = await getMessages(id);
            const nextMessages = Array.isArray(data) ? data : [];
            setMessages(nextMessages);

            const conv = conversationsRef.current.find(c => c.id === id);
            if (conv?.type === 'group') {
                const senderIds = Array.from(
                    new Set(nextMessages.map(m => m?.sender_id).filter(Boolean))
                );
                await Promise.all(senderIds.map(ensureUserProfileLoaded));
            }
        } catch (error) {
            console.error("Failed to load messages", error);
            toast.error("加载消息失败");
        }
    }, [ensureUserProfileLoaded]);

    const scrollToBottom = useCallback(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, []);

    const handleClickOutside = useCallback((event) => {
        if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
            setShowDropdown(false);
        }
        if (emojiPickerRef.current && !emojiPickerRef.current.contains(event.target) && !event.target.closest(`.${styles.attachBtn}`)) {
            setShowEmojiPicker(false);
        }
    }, []);

    // Socket initialization
    useEffect(() => {
        const socket = io('http://localhost:5001', {
            withCredentials: true,
            transports: ['websocket']
        });
        socketRef.current = socket;

        socket.on('connect', () => {
            console.log('Socket connected');
        });

        socket.on('new_message', (msg) => {
            console.log('New message:', msg);
            
            // 1. Update messages if looking at this conversation
            if (activeConvIdRef.current === msg.conversation_id) {
                const conv = conversationsRef.current.find(c => c.id === msg.conversation_id);
                if (conv?.type === 'group') {
                    ensureUserProfileLoaded(msg.sender_id);
                }
                setMessages(prev => {
                    if (prev.find(m => m.id === msg.id)) return prev;
                    return [...prev, msg];
                });
            }

            // 2. Update conversation list preview
            setConversations(prev => prev.map(c => {
                if (c.id === msg.conversation_id) {
                    return {
                        ...c,
                        last_message: {
                            content: msg.content,
                            created_at: msg.created_at
                        }
                    };
                }
                return c;
            }));
        });

        return () => {
            socket.disconnect();
        };
    }, [ensureUserProfileLoaded]);

    // Join/Leave conversation room
    useEffect(() => {
        if (activeConvId && socketRef.current) {
            socketRef.current.emit('join', { room: activeConvId });
            return () => {
                socketRef.current.emit('leave', { room: activeConvId });
            };
        }
    }, [activeConvId]);

    useEffect(() => {
        loadAllData();
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, [handleClickOutside, loadAllData]);

    useEffect(() => {
        if (activeConvId) {
            loadMessages(activeConvId);
            setNewMessage('');
            setSelectedFile(null);
        }
    }, [activeConvId, loadMessages]);

    useEffect(() => {
        scrollToBottom();
    }, [messages, scrollToBottom]);

    const handleFileSelect = (e) => {
        const file = e.target.files[0];
        if (!file) return;

        if (!file.type.startsWith('image/')) {
            toast.error('不支持的文件类型，请选择图片');
            return;
        }

        setSelectedFile(file);
        // Reset value so same file can be selected again if cleared
        e.target.value = '';
    };

    const removeFile = () => {
        setSelectedFile(null);
    };

    const handleEmojiClick = (emojiObject) => {
        setNewMessage(prev => prev + emojiObject.emoji);
    };

    const handleSend = async (e) => {
        e.preventDefault();
        if ((!newMessage.trim() && !selectedFile) || !activeConvId) return;

        try {
            let payload;
            if (selectedFile) {
                const formData = new FormData();
                formData.append('content', newMessage); // Caption
                formData.append('type', 'image');
                formData.append('media_file', selectedFile);
                payload = formData;
            } else {
                payload = newMessage; // Simple text
            }

            await sendMessage(activeConvId, payload);
            setNewMessage('');
            setSelectedFile(null);
            setShowEmojiPicker(false);
            
            // Optimistic update or wait for socket? 
            // Socket usually handles it, but let's reload to be safe or rely on socket.
            // Socket update is already handled in useEffect.
            
            // loadMessages(activeConvId); 
            // const convs = await getConversations();
            // setConversations(convs);
        } catch (error) {
            console.error("Failed to send message", error);
            toast.error("发送失败");
        }
    };
    
    const handleInput = (e) => {
        setNewMessage(e.target.value);
        e.target.style.height = 'auto';
        e.target.style.height = e.target.scrollHeight + 'px';
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend(e);
            e.target.style.height = 'auto';
        }
    };

    const handleAcceptRequest = async (id) => {
        try {
            await acceptFriendRequest(id);
            toast.success("已接受好友请求");
            loadAllData();
        } catch (err) {
            toast.error(err.message);
        }
    };

    const handleRejectRequest = async (id) => {
        try {
            await rejectFriendRequest(id);
            setRequests(prev => prev.filter(r => r.id !== id));
            toast.success("已拒绝好友请求");
        } catch (err) {
            toast.error(err.message);
        }
    };

    const refreshConversations = async () => {
        const convs = await getConversations();
        setConversations(Array.isArray(convs) ? convs : []);
        return convs;
    };

    const handleStartChat = async (friendId) => {
        try {
            const result = await createConversation(friendId);
            const convs = await refreshConversations();
            
            const convId = result.id || result.conversation_id;
            if (convId) {
                setActiveConvId(convId);
            } else {
                const target = convs.find(c => c.participants && c.participants.includes(friendId)); 
                if (target) setActiveConvId(target.id);
            }
        } catch (err) {
            console.error("Failed to start chat", err);
            toast.error("无法开始聊天");
        }
    };

    const getConvName = (conv) => {
        return conv.name || conv.other_user_name || "聊天";
    };

    const getConvAvatar = (conv) => {
        // Fallback logic if 'other_user_avatar' is not directly available, 
        // assumes backend might provide it or we use placeholder
        return conv.other_user_avatar || null;
    };
    
    const getOtherUserId = (conv) => {
        // Try to find the other user ID. 
        // If 'participants' is array of IDs and 'user.id' is known.
        if (conv.type === 'group') return null;
        if (conv.other_user_id) return conv.other_user_id;
        
        if (conv.participants && user) {
             const other = conv.participants.find(p => p !== user.id);
             return other;
        }
        return null;
    };

    const formatTime = (dateStr) => {
        if (!dateStr) return '';
        const date = new Date(dateStr);
        if (isNaN(date.getTime())) return '';
        
        const now = new Date();
        const diff = now - date;
        const oneDay = 24 * 60 * 60 * 1000;
        
        if (diff < oneDay && now.getDate() === date.getDate()) {
            return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false });
        } else if (diff < 7 * oneDay) {
            return date.toLocaleDateString([], { weekday: 'short' });
        } else {
            return date.toLocaleDateString([], { month: 'short', day: 'numeric' });
        }
    };

    const activeConv = conversations.find(c => c.id === activeConvId);
    const isGroupConv = activeConv?.type === 'group';
    const isGroupOwner = isGroupConv && user?.id && activeConv?.participants?.[0] === user.id;
    const otherUserId = activeConv ? getOtherUserId(activeConv) : null;

    const loadMemberProfiles = useCallback(async (participantIds) => {
        if (!participantIds || participantIds.length === 0) return;
        const missingIds = participantIds.filter(id => !memberProfilesRef.current[id] && !profileLoadInFlightRef.current.has(id));
        if (missingIds.length === 0) return;

        setMembersLoading(true);
        try {
            for (const id of missingIds) {
                profileLoadInFlightRef.current.add(id);
            }
            const entries = await Promise.all(missingIds.map(async (id) => {
                try {
                    const profile = await getUserProfile(id);
                    return [id, profile];
                } catch {
                    return [id, { id, username: id.slice(0, 6), profile: { avatar_url: null } }];
                }
            }));

            setMemberProfiles(prev => {
                const next = { ...prev };
                for (const [id, profile] of entries) {
                    if (!next[id]) next[id] = profile;
                }
                return next;
            });
        } finally {
            for (const id of missingIds) {
                profileLoadInFlightRef.current.delete(id);
            }
            setMembersLoading(false);
        }
    }, []);

    useEffect(() => {
        if (!showGroupMembers || !isGroupConv) return;
        loadMemberProfiles(activeConv?.participants || []);
        setInviteUserId('');
    }, [activeConv?.participants, isGroupConv, loadMemberProfiles, showGroupMembers]);

    useEffect(() => {
        if (!activeConvId) return;
        if (!isGroupConv) return;
        loadMemberProfiles(activeConv?.participants || []);
    }, [activeConv?.participants, activeConvId, isGroupConv, loadMemberProfiles]);

    const handleInviteToGroup = async () => {
        if (!activeConvId || !inviteUserId) return;
        setInviteSubmitting(true);
        try {
            await addGroupParticipant(activeConvId, inviteUserId);
            toast.success("已邀请进群");
            await refreshConversations();
            await loadMemberProfiles([inviteUserId]);
            setInviteUserId('');
        } catch (error) {
            const msg = error?.response?.data?.error || error?.message || '邀请失败';
            toast.error(msg);
        } finally {
            setInviteSubmitting(false);
        }
    };

    const handleKickFromGroup = async (targetId) => {
        if (!activeConvId || !targetId || targetId === user?.id) return;
        if (!isGroupOwner) {
            toast.error('只有群主可以踢人');
            return;
        }
        const confirmed = window.confirm('确定要将该成员移出群聊吗？');
        if (!confirmed) return;

        setRemovingUserId(targetId);
        try {
            await removeGroupParticipant(activeConvId, targetId);
            toast.success('已移出群聊');
            await refreshConversations();
        } catch (error) {
            const msg = error?.response?.data?.error || error?.message || '操作失败';
            toast.error(msg);
        } finally {
            setRemovingUserId(null);
        }
    };

    const handleLeaveGroup = async () => {
        if (!activeConvId || !user?.id) return;
        const confirmed = window.confirm('确定要退出该群聊吗？');
        if (!confirmed) return;

        setRemovingUserId(user.id);
        try {
            await removeGroupParticipant(activeConvId, user.id);
            toast.success('已退出群聊');
            setShowGroupMembers(false);
            setActiveConvId(null);
            await loadAllData();
        } catch (error) {
            const msg = error?.response?.data?.error || error?.message || '退群失败';
            toast.error(msg);
        } finally {
            setRemovingUserId(null);
        }
    };

    const invitableFriends = isGroupConv
        ? friends.filter(f => !activeConv?.participants?.includes(f.id))
        : [];

    return (
        <div className={`${styles.container} ${activeConvId ? styles.viewChat : ''}`}>
            {/* Left Sidebar */}
            <div className={styles.sidebar}>
                <div className={styles.sidebarHeader}>
                    <span className={styles.sidebarTitle}>消息</span>
                    <div className={styles.headerActions} ref={dropdownRef}>
                        <button className={styles.iconBtn} onClick={() => setShowDropdown(!showDropdown)}>
                            <Plus size={20} />
                        </button>
                        {showDropdown && (
                            <div className={styles.dropdownMenu}>
                                <button className={styles.dropdownItem} onClick={() => { setShowAddFriend(true); setShowDropdown(false); }}>
                                    <UserPlus size={16} />
                                    <span>添加好友</span>
                                </button>
                                <button className={styles.dropdownItem} onClick={() => { setShowCreateGroup(true); setShowDropdown(false); }}>
                                    <Users size={16} />
                                    <span>发起群聊</span>
                                </button>
                            </div>
                        )}
                    </div>
                </div>
                
                <div className={styles.conversationList}>
                    {/* Friend Requests */}
                    {requests.length > 0 && (
                        <>
                            <div className={styles.sectionTitle}>好友请求</div>
                            {requests.map(req => (
                                <div key={req.id} className={styles.listItem}>
                                    <div className={styles.avatar}>
                                        {req.other_user?.avatar ? (
                                            <img src={req.other_user.avatar} alt="" style={{ width: '100%', height: '100%', borderRadius: '50%' }} />
                                        ) : <User size={20} />}
                                    </div>
                                    <span className={styles.itemName}>{req.other_user?.name || "未知用户"}</span>
                                    <div className={styles.itemMeta} style={{display: 'flex', gap: 8}}>
                                        <button onClick={(e) => { e.stopPropagation(); handleAcceptRequest(req.id); }} style={{color: '#4ade80', background: 'none', border: 'none', cursor: 'pointer'}}><Check size={18}/></button>
                                        <button onClick={(e) => { e.stopPropagation(); handleRejectRequest(req.id); }} style={{color: '#f87171', background: 'none', border: 'none', cursor: 'pointer'}}><X size={18}/></button>
                                    </div>
                                    <span className={styles.itemPreview}>好友请求</span>
                                </div>
                            ))}
                        </>
                    )}

                    {/* Friends List */}
                    {friends.length > 0 && (
                        <>
                            <div className={styles.sectionTitle}>好友</div>
                            {friends.map(friend => (
                                <div key={friend.id} className={styles.listItem} onClick={() => handleStartChat(friend.id)}>
                                    <div className={styles.avatar}>
                                        {friend.avatar ? (
                                            <img src={friend.avatar} alt="" style={{ width: '100%', height: '100%', borderRadius: '50%' }} />
                                        ) : <User size={20} />}
                                    </div>
                                    <span className={styles.itemName}>{friend.name}</span>
                                    <span className={styles.itemPreview}>点击发起聊天</span>
                                </div>
                            ))}
                        </>
                    )}

                    {/* Conversations */}
                    <div className={styles.sectionTitle}>聊天</div>
                    {loading && <div className={styles.loadingContainer}><LoadingSpinner size="medium" /></div>}
                    {!loading && conversations.length === 0 && (
                        <div style={{ padding: '1rem', textAlign: 'center', color: '#94a3b8', fontSize: '0.9rem' }}>暂无聊天</div>
                    )}
                    
                    {conversations.map(conv => (
                        <div
                            key={conv.id}
                            className={`${styles.listItem} ${activeConvId === conv.id ? styles.active : ''}`}
                            onClick={() => setActiveConvId(conv.id)}
                        >
                            <div className={styles.avatar}>
                                {getConvAvatar(conv) ? (
                                    <img src={getConvAvatar(conv)} alt="" style={{ width: '100%', height: '100%' }} />
                                ) : (
                                    getConvName(conv).charAt(0).toUpperCase()
                                )}
                            </div>
                            <span className={styles.itemName}>{getConvName(conv)}</span>
                            <span className={styles.itemMeta}>
                                {conv.last_message ? formatTime(conv.last_message.created_at) : ''}
                            </span>
                            <span className={styles.itemPreview}>
                                {conv.last_message?.content || '暂无消息'}
                            </span>
                        </div>
                    ))}
                </div>
            </div>

            {/* Right Chat Area */}
            <div className={styles.chatArea}>
                {activeConvId ? (
                    <>
                        <div className={styles.chatHeader}>
                            <button className={styles.backButton} onClick={() => setActiveConvId(null)}>
                                <ArrowLeft size={24} />
                            </button>
                            <Link to={otherUserId ? `/profile/${otherUserId}` : '#'} className={styles.avatar} style={{width: 40, height: 40, fontSize: '1rem', textDecoration: 'none'}}>
                                {activeConv && getConvAvatar(activeConv) ? (
                                    <img src={getConvAvatar(activeConv)} alt="" style={{ width: '100%', height: '100%' }} />
                                ) : (
                                    getConvName(activeConv || {}).charAt(0).toUpperCase()
                                )}
                            </Link>
                            <Link to={otherUserId ? `/profile/${otherUserId}` : '#'} className={styles.headerInfo} style={{textDecoration: 'none'}}>
                                <span className={styles.headerName}>
                                    {activeConv ? getConvName(activeConv) : '聊天'}
                                </span>
                                <span className={styles.headerStatus}>在线</span>
                            </Link>
                            {isGroupConv && (
                                <div style={{ marginLeft: 'auto' }}>
                                    <button
                                        type="button"
                                        className={styles.iconBtn}
                                        title="群成员"
                                        onClick={() => setShowGroupMembers(true)}
                                    >
                                        <Users size={20} />
                                    </button>
                                </div>
                            )}
                        </div>

                        <div className={styles.messages}>
                            {messages.map((msg, index) => {
                                const isMe = msg.sender_id === user?.id;
                                const prevMsg = messages[index - 1];
                                const isChain = prevMsg && prevMsg.sender_id === msg.sender_id;
                                const senderProfile = isGroupConv ? memberProfiles[msg.sender_id] : null;
                                const senderAvatar = isMe ? user?.profile?.avatar_url : senderProfile?.profile?.avatar_url;
                                const senderName = isMe ? (user?.username || '我') : (senderProfile?.username || msg.sender_id?.slice(0, 6) || 'U');
                                
                                return (
                                    <div 
                                        key={msg.id || index} 
                                        className={`${styles.messageRow} ${isMe ? styles.me : ''}`}
                                        data-chain={!isChain ? "first" : ""}
                                    >
                                        {!isMe && isGroupConv && (
                                            <div className={styles.msgAvatar} title={senderName}>
                                                {senderAvatar ? (
                                                    <img src={senderAvatar} alt="" className={styles.msgAvatarImg} />
                                                ) : (
                                                    <span className={styles.msgAvatarFallback}>{senderName.charAt(0).toUpperCase()}</span>
                                                )}
                                            </div>
                                        )}
                                        <div className={styles.messageBubble}>
                                            {msg.type === 'image' ? (
                                                <div className={styles.imageMessage}>
                                                    <img src={msg.media_url} alt="Shared" className={styles.msgImage} />
                                                    {msg.content && <p className={styles.imageCaption}>{msg.content}</p>}
                                                </div>
                                            ) : msg.type === 'share_post' ? (
                                                <div className={styles.shareMessage}>
                                                    <p className={styles.shareText}>{msg.content}</p>
                                                    <Link to={`/social/post/${msg.reference_id}`} className={styles.shareLink}>
                                                        <div className={styles.shareCard}>
                                                            <span>查看分享的帖子</span>
                                                            <ArrowLeft size={16} style={{transform: 'rotate(180deg)'}} />
                                                        </div>
                                                    </Link>
                                                </div>
                                            ) : (
                                                msg.content
                                            )}
                                        </div>
                                        {isMe && isGroupConv && (
                                            <div className={styles.msgAvatar} title={senderName}>
                                                {senderAvatar ? (
                                                    <img src={senderAvatar} alt="" className={styles.msgAvatarImg} />
                                                ) : (
                                                    <span className={styles.msgAvatarFallback}>{senderName.charAt(0).toUpperCase()}</span>
                                                )}
                                            </div>
                                        )}
                                    </div>
                                );
                            })}
                            <div ref={messagesEndRef} />
                        </div>

                        <div className={styles.inputContainer}>
                            {selectedFile && (
                                <div className={styles.filePreview}>
                                    <div className={styles.previewItem}>
                                        <ImageIcon size={16} />
                                        <span className={styles.fileName}>{selectedFile.name}</span>
                                        <button type="button" onClick={removeFile} className={styles.removeFileBtn}>
                                            <X size={14} />
                                        </button>
                                    </div>
                                </div>
                            )}
                            
                            <form onSubmit={handleSend} className={styles.inputWrapper}>
                                <input 
                                    type="file" 
                                    ref={fileInputRef}
                                    style={{display: 'none'}} 
                                    accept="image/*"
                                    onChange={handleFileSelect}
                                />
                                <button type="button" className={styles.attachBtn} onClick={() => fileInputRef.current?.click()}>
                                    <ImageIcon size={20} />
                                </button>
                                <textarea
                                    value={newMessage}
                                    onChange={handleInput}
                                    onKeyDown={handleKeyDown}
                                    placeholder="Message..."
                                    className={styles.inputField}
                                    rows={1}
                                />
                                <div className={styles.emojiWrapper} ref={emojiPickerRef}>
                                    <button 
                                        type="button" 
                                        className={styles.attachBtn} 
                                        onClick={() => setShowEmojiPicker(!showEmojiPicker)}
                                    >
                                        <Smile size={20} />
                                    </button>
                                    {showEmojiPicker && (
                                        <div className={styles.emojiPickerContainer}>
                                            <EmojiPicker onEmojiClick={handleEmojiClick} width={300} height={400} />
                                        </div>
                                    )}
                                </div>
                                <button type="submit" className={styles.sendBtn} disabled={!newMessage.trim() && !selectedFile}>
                                    <Send size={20} />
                                </button>
                            </form>
                        </div>
                    </>
                ) : (
                    <div className={styles.noChat}>
                        <div className={styles.noChatIcon}>
                            <MessageSquare size={32} />
                        </div>
                        <p>选择一个聊天开始发送消息</p>
                    </div>
                )}
            </div>

            {showAddFriend && <AddFriendModal onClose={() => setShowAddFriend(false)} />}
            {showCreateGroup && (
                <CreateGroupModal 
                    onClose={() => setShowCreateGroup(false)} 
                    onSuccess={loadAllData} 
                />
            )}
            {showGroupMembers && isGroupConv && (
                <Modal
                    title={`群成员（${activeConv?.participants?.length || 0}）`}
                    isOpen={true}
                    onClose={() => setShowGroupMembers(false)}
                    className={styles.groupModal}
                >
                    <div className={styles.groupSection}>
                        <div className={styles.groupSectionTitle}>拉人进群</div>
                        <div className={styles.groupInviteRow}>
                            <select
                                className={styles.groupSelect}
                                value={inviteUserId}
                                onChange={(e) => setInviteUserId(e.target.value)}
                                disabled={inviteSubmitting || invitableFriends.length === 0}
                            >
                                <option value="">
                                    {invitableFriends.length === 0 ? '暂无可邀请好友' : '选择好友...'}
                                </option>
                                {invitableFriends.map(f => (
                                    <option key={f.id} value={f.id}>
                                        {f.name}
                                    </option>
                                ))}
                            </select>
                            <button
                                type="button"
                                className={styles.primaryActionBtn}
                                onClick={handleInviteToGroup}
                                disabled={inviteSubmitting || !inviteUserId}
                            >
                                邀请
                            </button>
                        </div>
                    </div>

                    <div className={styles.groupSection}>
                        <div className={styles.groupSectionTitle}>成员列表</div>
                        <div className={styles.memberList}>
                            {(activeConv?.participants || []).map(pid => {
                                const p = memberProfiles[pid];
                                const displayName = p?.username || pid.slice(0, 6);
                                const avatarUrl = p?.profile?.avatar_url;
                                const isMe = pid === user?.id;

                                return (
                                    <div key={pid} className={styles.memberRow}>
                                        <div className={styles.memberLeft}>
                                            <div className={styles.memberAvatar}>
                                                {avatarUrl ? (
                                                    <img src={avatarUrl} alt="" />
                                                ) : (
                                                    <span>{displayName.charAt(0).toUpperCase()}</span>
                                                )}
                                            </div>
                                            <div className={styles.memberInfo}>
                                                <div className={styles.memberName}>
                                                    {displayName}
                                                    {isMe && <span className={styles.meBadge}>我</span>}
                                                </div>
                                                <div className={styles.memberSub}>{pid}</div>
                                            </div>
                                        </div>

                                        {isGroupOwner && !isMe && (
                                            <button
                                                type="button"
                                                className={styles.dangerActionBtn}
                                                onClick={() => handleKickFromGroup(pid)}
                                                disabled={removingUserId === pid || membersLoading}
                                            >
                                                踢出
                                            </button>
                                        )}
                                    </div>
                                );
                            })}

                            {membersLoading && (
                                <div className={styles.memberLoading}>加载成员信息中...</div>
                            )}
                        </div>
                    </div>

                    <div className={styles.groupFooter}>
                        <button
                            type="button"
                            className={styles.leaveBtn}
                            onClick={handleLeaveGroup}
                            disabled={removingUserId === user?.id}
                        >
                            退出群聊
                        </button>
                    </div>
                </Modal>
            )}
        </div>
    );
};

export default ChatPage;
