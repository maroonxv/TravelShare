import { useState, useEffect } from 'react';
import { getFriendRequests, acceptFriendRequest, rejectFriendRequest } from '../api/social';
import Button from './Button';
import { Check, X } from 'lucide-react';
import { toast } from 'react-hot-toast';

const FriendRequestsList = () => {
    const [requests, setRequests] = useState([]);

    useEffect(() => {
        loadRequests();
    }, []);

    const loadRequests = async () => {
        try {
            const data = await getFriendRequests('incoming');
            setRequests(Array.isArray(data) ? data : []);
        } catch (error) {
            console.error(error);
        }
    };

    const handleAccept = async (id) => {
        try {
            await acceptFriendRequest(id);
            setRequests(prev => prev.filter(r => r.id !== id));
            toast.success("已接受");
        } catch (err) {
            toast.error(err.message);
        }
    };

    const handleReject = async (id) => {
        try {
            await rejectFriendRequest(id);
            setRequests(prev => prev.filter(r => r.id !== id));
            toast.success("已拒绝");
        } catch (err) {
            toast.error(err.message);
        }
    };

    if (requests.length === 0) return null; // Don't show if empty

    return (
        <div style={{ padding: '0 10px 10px' }}>
            {requests.map(req => (
                <div key={req.id} style={{
                    display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                    padding: '8px', background: 'rgba(255,255,255,0.05)', borderRadius: '8px', marginBottom: '5px'
                }}>
                    <span style={{ fontSize: '0.9em' }}>
                        Request from <strong>{req.other_user?.name || req.requester_id.substring(0, 6)}</strong>
                    </span>
                    <div style={{ display: 'flex', gap: '5px' }}>
                        <button onClick={() => handleAccept(req.id)} style={{ border: 'none', background: 'green', color: '#fff', borderRadius: '4px', cursor: 'pointer' }}><Check size={14} /></button>
                        <button onClick={() => handleReject(req.id)} style={{ border: 'none', background: 'red', color: '#fff', borderRadius: '4px', cursor: 'pointer' }}><X size={14} /></button>
                    </div>
                </div>
            ))}
        </div>
    );
};

export default FriendRequestsList;
