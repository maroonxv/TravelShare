import { useState, useEffect, useCallback } from 'react';
import Button from './Button';
import { UserPlus, UserCheck, Clock, MessageSquare, X } from 'lucide-react';
import { sendFriendRequest, acceptFriendRequest, rejectFriendRequest, getFriendshipStatus } from '../api/social';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-hot-toast';

const FriendActionButton = ({ targetUserId, initialStatus }) => {
    // initialStatus passed from parent if available, else fetch
    const [status, setStatus] = useState(initialStatus?.status || null);
    const [isRequester, setIsRequester] = useState(initialStatus?.is_requester || false);
    const [friendshipId, setFriendshipId] = useState(initialStatus?.id || null);
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    // Fetch status if not provided or to refresh
    const fetchStatus = useCallback(async () => {
        try {
            const res = await getFriendshipStatus(targetUserId);
            setStatus(res.status);
            setIsRequester(res.is_requester);
            setFriendshipId(res.id);
        } catch (err) {
            console.error(err);
        }
    }, [targetUserId]);

    useEffect(() => {
        if (!initialStatus) {
            fetchStatus();
        }
    }, [fetchStatus, initialStatus]);

    const handleAddFriend = async () => {
        setLoading(true);
        try {
            const res = await sendFriendRequest(targetUserId);
            setStatus(res.status); // PENDING
            setIsRequester(true);
            setFriendshipId(res.friendship_id);
            toast.success("好友请求已发送");
        } catch (err) {
            toast.error("发送请求失败: " + (err.response?.data?.error || err.message));
        } finally {
            setLoading(false);
        }
    };

    const handleAccept = async () => {
        setLoading(true);
        try {
            await acceptFriendRequest(friendshipId);
            setStatus('ACCEPTED');
            toast.success("已接受好友请求");
        } catch (err) {
            toast.error("接受请求失败: " + err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleReject = async () => {
        setLoading(true);
        try {
            await rejectFriendRequest(friendshipId);
            setStatus('REJECTED'); // Or reset to null depending on UX.
            toast.success("已拒绝好友请求");
        } catch (err) {
            toast.error("拒绝请求失败: " + err.message);
        } finally {
            setLoading(false);
        }
    };

    if (loading) return <Button disabled>处理中...</Button>;

    if (status === 'ACCEPTED') {
        return (
            <Button onClick={() => navigate('/chat')} icon={<MessageSquare size={18} />}>
                发消息
            </Button>
        );
    }

    if (status === 'PENDING') {
        if (isRequester) {
            return (
                <Button disabled variant="secondary" icon={<Clock size={18} />}>
                    请求已发送
                </Button>
            );
        } else {
            return (
                <div style={{ display: 'flex', gap: '8px' }}>
                    <Button onClick={handleAccept} icon={<UserCheck size={18} />}>
                        接受请求
                    </Button>
                    <Button onClick={handleReject} variant="danger" icon={<X size={18} />}>
                        拒绝
                    </Button>
                </div>
            );
        }
    }

    if (status === 'REJECTED') {
        return <Button disabled variant="secondary">已拒绝</Button>;
    }

    if (status === 'BLOCKED') {
        return <Button disabled variant="secondary">不可用</Button>;
    }

    // Default: No status
    return (
        <Button onClick={handleAddFriend} icon={<UserPlus size={18} />}>
            添加好友
        </Button>
    );
};

export default FriendActionButton;
