import { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import styles from './ProfilePage.module.css';
import Button from '../../components/Button';
import Input from '../../components/Input';
import Card from '../../components/Card';
import { User, MapPin, Mail, Shield } from 'lucide-react';

const ProfilePage = () => {
    const { user, updatePassword } = useAuth();
    const [passData, setPassData] = useState({ oldPassword: '', newPassword: '', confirmPassword: '' });
    const [message, setMessage] = useState({ type: '', text: '' });
    const [loading, setLoading] = useState(false);

    const handlePasswordChange = async (e) => {
        e.preventDefault();
        if (passData.newPassword !== passData.confirmPassword) {
            setMessage({ type: 'error', text: 'New passwords do not match' });
            return;
        }

        setLoading(true);
        setMessage({ type: '', text: '' });
        try {
            await updatePassword(passData.oldPassword, passData.newPassword);
            setMessage({ type: 'success', text: 'Password updated successfully' });
            setPassData({ oldPassword: '', newPassword: '', confirmPassword: '' });
        } catch (error) {
            setMessage({ type: 'error', text: 'Failed to update password' });
        } finally {
            setLoading(false);
        }
    };

    if (!user) return <div>Loading...</div>;

    return (
        <div className={styles.container}>
            <div className={styles.header}>
                <div className={styles.avatar}>
                    {user.username?.charAt(0).toUpperCase() || 'U'}
                </div>
                <div className={styles.userInfo}>
                    <h1>{user.username}</h1>
                    <p className={styles.role}>{user.role}</p>
                </div>
            </div>

            <div className={styles.grid}>
                <Card title="Personal Info" className={styles.infoCard}>
                    <div className={styles.infoRow}>
                        <Mail size={18} />
                        <span>{user.email}</span>
                    </div>
                    <div className={styles.infoRow}>
                        <User size={18} />
                        <span>@{user.username}</span>
                    </div>
                    {user.profile?.location && (
                        <div className={styles.infoRow}>
                            <MapPin size={18} />
                            <span>{user.profile.location}</span>
                        </div>
                    )}
                    <div className={styles.infoRow}>
                        <Shield size={18} />
                        <span>Role: {user.role}</span>
                    </div>
                    {user.profile?.bio && (
                        <div className={styles.bio}>
                            <h3>Bio</h3>
                            <p>{user.profile.bio}</p>
                        </div>
                    )}
                </Card>

                <Card title="Change Password" className={styles.passwordCard}>
                    <form onSubmit={handlePasswordChange}>
                        <Input
                            label="Current Password"
                            type="password"
                            value={passData.oldPassword}
                            onChange={(e) => setPassData({ ...passData, oldPassword: e.target.value })}
                            required
                        />
                        <Input
                            label="New Password"
                            type="password"
                            value={passData.newPassword}
                            onChange={(e) => setPassData({ ...passData, newPassword: e.target.value })}
                            required
                        />
                        <Input
                            label="Confirm New Password"
                            type="password"
                            value={passData.confirmPassword}
                            onChange={(e) => setPassData({ ...passData, confirmPassword: e.target.value })}
                            required
                        />

                        {message.text && (
                            <div className={`${styles.message} ${styles[message.type]}`}>
                                {message.text}
                            </div>
                        )}

                        <Button type="submit" variant="primary" disabled={loading} style={{ width: '100%', marginTop: '1rem' }}>
                            {loading ? 'Updating...' : 'Update Password'}
                        </Button>
                    </form>
                </Card>
            </div>
        </div>
    );
};

export default ProfilePage;
