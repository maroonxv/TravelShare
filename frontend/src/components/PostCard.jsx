import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
    ChevronLeft,
    ChevronRight,
    FileText,
    Heart,
    Image as ImageIcon,
    MapPin,
    MessageCircle,
    Share2,
    Trash2,
} from 'lucide-react';
import { toast } from 'react-hot-toast';
import { deletePost, likePost } from '../api/social';
import { useAuth } from '../context/useAuth';
import Card from './Card';
import ShareModal from '../pages/social/ShareModal';
import styles from './PostCard.module.css';

const PostCard = ({ post, onDelete }) => {
    const { user } = useAuth();
    const navigate = useNavigate();
    const [likes, setLikes] = useState(post.like_count || 0);
    const [isLiked, setIsLiked] = useState(post.is_liked || false);
    const [isDeleting, setIsDeleting] = useState(false);
    const [isExpanded, setIsExpanded] = useState(false);
    const [showShareModal, setShowShareModal] = useState(false);
    const [currentImageIndex, setCurrentImageIndex] = useState(0);

    const handlePrevImage = (e) => {
        e.stopPropagation();
        setCurrentImageIndex((prev) => (prev === 0 ? post.media_urls.length - 1 : prev - 1));
    };

    const handleNextImage = (e) => {
        e.stopPropagation();
        setCurrentImageIndex((prev) => (prev === post.media_urls.length - 1 ? 0 : prev + 1));
    };

    const handleLike = async () => {
        try {
            const data = await likePost(post.id);
            setIsLiked(data.is_liked);
            setLikes((prev) => (data.is_liked ? prev + 1 : prev - 1));
        } catch (error) {
            console.error('Failed to like post', error);
            toast.error('操作失败');
        }
    };

    const handleDelete = async () => {
        if (!window.confirm('确定要删除这条动态吗？')) return;
        setIsDeleting(true);
        try {
            await deletePost(post.id);
            toast.success('动态已删除');
            if (onDelete) {
                onDelete(post.id);
            } else {
                window.location.reload();
            }
        } catch (error) {
            console.error('Failed to delete post', error);
            toast.error('删除失败');
            setIsDeleting(false);
        }
    };

    const handleImageClick = (e) => {
        e.preventDefault();
        navigate(`/social/post/${post.id}`);
    };

    const renderMediaArea = () => {
        const hasMedia = post.media_urls && post.media_urls.length > 0;

        if (hasMedia) {
            return (
                <div className={styles.mediaArea} onClick={handleImageClick} style={{ cursor: 'pointer' }}>
                    <img
                        src={post.media_urls[currentImageIndex]}
                        alt={`Post media ${currentImageIndex + 1}`}
                        className={styles.mediaCover}
                    />
                    {post.media_urls.length > 1 && (
                        <>
                            <button className={`${styles.navBtn} ${styles.navBtnPrev}`} onClick={handlePrevImage} type="button">
                                <ChevronLeft size={18} />
                            </button>
                            <button className={`${styles.navBtn} ${styles.navBtnNext}`} onClick={handleNextImage} type="button">
                                <ChevronRight size={18} />
                            </button>
                            <div className={styles.imageBadge}>
                                <ImageIcon size={12} />
                                <span>
                                    {currentImageIndex + 1}/{post.media_urls.length}
                                </span>
                            </div>
                        </>
                    )}
                </div>
            );
        }

        return (
            <div className={styles.mediaArea}>
                <div className={styles.placeholder}>
                    <div className={styles.placeholderIcon}>
                        {post.trip ? <MapPin size={28} /> : <FileText size={28} />}
                    </div>
                    <div className={styles.placeholderText}>{post.title || post.content}</div>
                </div>
            </div>
        );
    };

    return (
        <Card className={styles.postCard}>
            {renderMediaArea()}

            <div className={styles.header}>
                <Link to={`/profile/${post.author_id}`} className={styles.userInfo}>
                    <div className={styles.avatar}>
                        {post.author_avatar ? (
                            <img src={post.author_avatar} alt={post.author_name} className={styles.avatarImage} />
                        ) : (
                            post.author_name?.charAt(0).toUpperCase()
                        )}
                    </div>
                    <div className={styles.userMeta}>
                        <div className={styles.username}>{post.author_name}</div>
                        <div className={styles.date}>{new Date(post.created_at).toLocaleDateString()}</div>
                    </div>
                </Link>

                {user && user.id === post.author_id && (
                    <button
                        onClick={handleDelete}
                        disabled={isDeleting}
                        className={styles.deleteBtn}
                        title="删除动态"
                        type="button"
                    >
                        <Trash2 size={16} />
                    </button>
                )}
            </div>

            <div className={styles.content}>
                <Link to={`/social/post/${post.id}`} className={styles.titleLink}>
                    <h3 className={styles.title}>{post.title || '未命名动态'}</h3>
                </Link>

                <div className={styles.textContainer}>
                    <p className={`${styles.text} ${!isExpanded ? styles.textCollapsed : ''}`}>{post.content}</p>
                    {post.content && post.content.length > 100 && (
                        <button className={styles.expandBtn} onClick={() => setIsExpanded(!isExpanded)} type="button">
                            {isExpanded ? '收起' : '展开全文'}
                        </button>
                    )}
                </div>

                {post.trip && (
                    <div className={styles.tripLink}>
                        <MapPin size={14} />
                        {post.trip.is_public ? (
                            <Link to={`/travel/${post.trip.id}`}>{post.trip.title}</Link>
                        ) : (
                            <span>{post.trip.title}</span>
                        )}
                    </div>
                )}

                {post.tags && post.tags.length > 0 && (
                    <div className={styles.tags}>
                        {post.tags.map((tag, idx) => (
                            <Link key={idx} to={`/social?tag=${tag}`} className={styles.tag}>
                                #{tag}
                            </Link>
                        ))}
                    </div>
                )}
            </div>

            <div className={styles.actions}>
                <button className={`${styles.actionBtn} ${isLiked ? styles.actionLiked : ''}`} onClick={handleLike} type="button">
                    <Heart size={18} fill={isLiked ? 'currentColor' : 'none'} />
                    <span>{likes || '点赞'}</span>
                </button>
                <Link to={`/social/post/${post.id}`} className={styles.actionBtn}>
                    <MessageCircle size={18} />
                    <span>{post.comment_count || '评论'}</span>
                </Link>
                <button className={styles.actionBtn} onClick={() => setShowShareModal(true)} type="button">
                    <Share2 size={18} />
                    <span>分享</span>
                </button>
            </div>

            <ShareModal isOpen={showShareModal} onClose={() => setShowShareModal(false)} post={post} />
        </Card>
    );
};

export default PostCard;
