import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import styles from './ProfilePage.module.css'; // Reuse profile styles for consistency
import Button from '../../components/Button';
import Input from '../../components/Input';
import Card from '../../components/Card';
import LoadingSpinner from '../../components/LoadingSpinner';
import { toast } from 'react-hot-toast';
import { Save, Lock, User, ArrowLeft } from 'lucide-react';

const ManageProfilePage = () => {
    const { user, updatePassword, updateProfile } = useAuth();
    const navigate = useNavigate();
    
    // Profile State
    const [profileData, setProfileData] = useState({
        bio: '',
        location: ''
    });
    const [avatarFile, setAvatarFile] = useState(null);
    const [avatarPreview, setAvatarPreview] = useState(null);
    
    // Password State
    const [passData, setPassData] = useState({ 
        oldPassword: '', 
        newPassword: '', 
        confirmPassword: '' 
    });
    
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (user?.profile) {
            setProfileData({
                bio: user.profile.bio || '',
                location: user.profile.location || ''
            });
            if (user.profile.avatar_url) {
                setAvatarPreview(user.profile.avatar_url);
            }
        }
    }, [user]);

    const handleFileChange = (e) => {
        const file = e.target.files[0];
        if (file) {
            setAvatarFile(file);
            const reader = new FileReader();
            reader.onloadend = () => {
                setAvatarPreview(reader.result);
            };
            reader.readAsDataURL(file);
        }
    };

    const handleProfileUpdate = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            const formData = new FormData();
            formData.append('bio', profileData.bio);
            formData.append('location', profileData.location);
            if (avatarFile) {
                formData.append('avatar', avatarFile);
            } else if (avatarPreview && user.profile.avatar_url === avatarPreview) {
                // Keep existing avatar URL if no new file
                formData.append('avatar_url', user.profile.avatar_url);
            }

            await updateProfile(formData);
            toast.success("个人资料已更新");
        } catch (error) {
            toast.error(error.response?.data?.error || '更新失败');
        } finally {
            setLoading(false);
        }
    };

    const handlePasswordChange = async (e) => {
        e.preventDefault();
        if (passData.newPassword !== passData.confirmPassword) {
            toast.error("新密码不匹配");
            return;
        }

        setLoading(true);
        try {
            await updatePassword(passData.oldPassword, passData.newPassword);
            toast.success("密码修改成功");
            setPassData({ oldPassword: '', newPassword: '', confirmPassword: '' });
        } catch (error) {
            toast.error(error.response?.data?.error || '密码修改失败');
        } finally {
            setLoading(false);
        }
    };

    if (!user) return <div className={styles.loadingContainer}><LoadingSpinner size="large" /></div>;

    return (
        <div className={styles.container}>
            <Button 
                variant="ghost" 
                onClick={() => navigate('/profile')}
                className={styles.backButton}
            >
                <ArrowLeft size={20} /> 返回个人主页
            </Button>
            
            <div className={styles.header}>
                <div className={styles.userInfo}>
                    <h1>管理个人资料</h1>
                    <p className={styles.role}>设置与安全</p>
                </div>
            </div>

            <div className={styles.grid}>
                <Card title="基本资料" className={styles.infoCard}>
                    <form onSubmit={handleProfileUpdate}>
                        <div className={styles.avatarUploadContainer}>
                            <div className={styles.avatarPreview}>
                                {avatarPreview ? (
                                    <img src={avatarPreview} alt="Avatar" className={styles.avatarImage} />
                                ) : (
                                    <User size={48} color="#9ca3af" />
                                )}
                            </div>
                            <label htmlFor="avatar-upload" className={styles.avatarLabel}>
                                更换头像
                            </label>
                            <input 
                                id="avatar-upload" 
                                type="file" 
                                accept="image/*" 
                                onChange={handleFileChange} 
                                style={{ display: 'none' }} 
                            />
                        </div>

                        <Input
                            label="居住地"
                            value={profileData.location}
                            onChange={(e) => setProfileData({ ...profileData, location: e.target.value })}
                            icon={<User size={18} />}
                            placeholder="例如：北京"
                        />
                        <div style={{ marginBottom: '1rem' }}>
                            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 500, color: 'var(--text-secondary)' }}>简介</label>
                            <textarea
                                value={profileData.bio}
                                onChange={(e) => setProfileData({ ...profileData, bio: e.target.value })}
                                className={styles.textarea}
                                placeholder="介绍一下你自己..."
                            />
                        </div>
                        <Button type="submit" disabled={loading} fullWidth icon={<Save size={18} />}>
                            {loading ? '保存中...' : '保存资料'}
                        </Button>
                    </form>
                </Card>

                <Card title="安全设置" className={styles.passwordCard}>
                    <form onSubmit={handlePasswordChange}>
                        <Input
                            label="当前密码"
                            type="password"
                            value={passData.oldPassword}
                            onChange={(e) => setPassData({ ...passData, oldPassword: e.target.value })}
                            required
                            icon={<Lock size={18} />}
                        />
                        <Input
                            label="新密码"
                            type="password"
                            value={passData.newPassword}
                            onChange={(e) => setPassData({ ...passData, newPassword: e.target.value })}
                            required
                            icon={<Lock size={18} />}
                        />
                        <Input
                            label="确认新密码"
                            type="password"
                            value={passData.confirmPassword}
                            onChange={(e) => setPassData({ ...passData, confirmPassword: e.target.value })}
                            required
                            icon={<Lock size={18} />}
                        />
                        <Button type="submit" disabled={loading} fullWidth variant="secondary">
                            {loading ? '保存中...' : '修改密码'}
                        </Button>
                    </form>
                </Card>
            </div>
        </div>
    );
};

export default ManageProfilePage;
