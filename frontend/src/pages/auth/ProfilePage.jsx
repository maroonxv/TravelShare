import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { Mail, MapPin, Settings, Shield, User } from 'lucide-react';
import { useAuth } from '../../context/useAuth';
import { getUserPosts, getUserProfile } from '../../api/social';
import { getUserTrips } from '../../api/travel';
import Button from '../../components/Button';
import Card from '../../components/Card';
import FriendActionButton from '../../components/FriendActionButton';
import LoadingSpinner from '../../components/LoadingSpinner';
import PostCard from '../../components/PostCard';
import TripCard from '../../components/TripCard';
import styles from './ProfilePage.module.css';

const ProfilePage = () => {
    const { user: currentUser } = useAuth();
    const { userId } = useParams();
    const [viewUser, setViewUser] = useState(null);
    const [posts, setPosts] = useState([]);
    const [trips, setTrips] = useState([]);
    const [loading, setLoading] = useState(true);

    const isOwnProfile = !userId || (currentUser && userId === currentUser.id);

    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            try {
                const targetUserId = userId || currentUser?.id;
                if (!targetUserId) {
                    setLoading(false);
                    return;
                }

                const targetUser = isOwnProfile ? currentUser : await getUserProfile(userId);
                setViewUser(targetUser);

                if (targetUser) {
                    const [postsData, tripsData] = await Promise.all([
                        getUserPosts(targetUser.id),
                        getUserTrips(targetUser.id),
                    ]);
                    setPosts(Array.isArray(postsData) ? postsData : postsData.posts || []);
                    setTrips(tripsData || []);
                }
            } catch (error) {
                console.error('Failed to fetch user data', error);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [userId, currentUser, isOwnProfile]);

    if (loading) {
        return (
            <div className={styles.loadingContainer}>
                <LoadingSpinner size="large" />
            </div>
        );
    }

    if (!viewUser) return <div className={styles.loadingContainer}>用户不存在</div>;

    return (
        <div className={styles.container}>
            <div className={styles.header}>
                <div className={styles.avatar}>
                    {viewUser.profile?.avatar_url ? (
                        <img src={viewUser.profile.avatar_url} alt={viewUser.username} className={styles.avatarImage} />
                    ) : (
                        viewUser.username?.charAt(0).toUpperCase() || 'U'
                    )}
                </div>

                <div className={styles.userInfo}>
                    <h1>{viewUser.username}</h1>
                    <p className={styles.role}>{viewUser.role === 'admin' ? '管理员账号' : '旅行用户'}</p>
                </div>

                <div className={styles.actionButtons}>
                    {!isOwnProfile ? (
                        <FriendActionButton targetUserId={viewUser.id} initialStatus={viewUser.friendship} />
                    ) : (
                        <Link to="/profile/edit">
                            <Button variant="secondary" icon={<Settings size={16} />}>
                                编辑资料
                            </Button>
                        </Link>
                    )}
                </div>
            </div>

            <div className={styles.grid}>
                <Card title="个人信息" className={styles.infoCard}>
                    {isOwnProfile && (
                        <div className={styles.infoRow}>
                            <Mail size={18} />
                            <span>{viewUser.email}</span>
                        </div>
                    )}
                    <div className={styles.infoRow}>
                        <User size={18} />
                        <span>@{viewUser.username}</span>
                    </div>
                    {viewUser.profile?.location && (
                        <div className={styles.infoRow}>
                            <MapPin size={18} />
                            <span>{viewUser.profile.location}</span>
                        </div>
                    )}
                    <div className={styles.infoRow}>
                        <Shield size={18} />
                        <span>角色：{viewUser.role}</span>
                    </div>
                    {viewUser.profile?.bio && (
                        <div className={styles.bio}>
                            <h3>简介</h3>
                            <p>{viewUser.profile.bio}</p>
                        </div>
                    )}
                </Card>

                <Card title="概览" className={styles.infoCard}>
                    <div className={styles.infoRow}>
                        <span>动态数量</span>
                        <span>{posts.length}</span>
                    </div>
                    <div className={styles.infoRow}>
                        <span>行程数量</span>
                        <span>{trips.length}</span>
                    </div>
                    <div className={styles.infoRow}>
                        <span>最近状态</span>
                        <span>{isOwnProfile ? '可管理' : '可浏览'}</span>
                    </div>
                </Card>
            </div>

            {posts.length > 0 && (
                <>
                    <h2 className={styles.sectionTitle}>{isOwnProfile ? '我的动态' : '动态记录'}</h2>
                    <div className={styles.itemsGrid}>
                        {posts.map((post) => (
                            <PostCard key={post.id} post={post} />
                        ))}
                    </div>
                </>
            )}

            {trips.length > 0 && (
                <>
                    <h2 className={styles.sectionTitle}>{isOwnProfile ? '我的行程' : '公开行程'}</h2>
                    <div className={styles.itemsGrid}>
                        {trips.map((trip) => (
                            <TripCard key={trip.id} trip={trip} />
                        ))}
                    </div>
                </>
            )}
        </div>
    );
};

export default ProfilePage;
