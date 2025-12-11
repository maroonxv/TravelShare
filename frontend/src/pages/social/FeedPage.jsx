import { useState, useEffect } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { Plus, X } from 'lucide-react';
import { getFeed } from '../../api/social';
import PostCard from '../../components/PostCard';
import Button from '../../components/Button';
import styles from './FeedPage.module.css';

const FeedPage = () => {
    const [searchParams, setSearchParams] = useSearchParams();
    const currentTag = searchParams.get('tag');

    const [posts, setPosts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [offset, setOffset] = useState(0);
    const [hasMore, setHasMore] = useState(true);
    const LIMIT = 10;

    useEffect(() => {
        const loadInitial = async () => {
            setLoading(true);
            try {
                const tags = currentTag ? [currentTag] : [];
                const data = await getFeed(LIMIT, 0, tags);
                const newPosts = Array.isArray(data) ? data : (data.posts || []);
                setPosts(newPosts);
                setOffset(LIMIT);
                setHasMore(newPosts.length === LIMIT);
            } catch (error) {
                console.error('Failed to fetch feed', error);
            } finally {
                setLoading(false);
            }
        };
        loadInitial();
    }, [currentTag]);

    const handleLoadMore = async () => {
        if (loading) return;
        setLoading(true);
        try {
            const tags = currentTag ? [currentTag] : [];
            const data = await getFeed(LIMIT, offset, tags);
            const newPosts = Array.isArray(data) ? data : (data.posts || []);

            setPosts(prev => {
                const existingIds = new Set(prev.map(p => p.id));
                const uniqueNewPosts = newPosts.filter(p => !existingIds.has(p.id));
                return [...prev, ...uniqueNewPosts];
            });
            setOffset(prev => prev + LIMIT);
            setHasMore(newPosts.length === LIMIT);
        } catch (error) {
            console.error('Failed to fetch more posts', error);
        } finally {
            setLoading(false);
        }
    };

    const clearTag = () => {
        setSearchParams({});
    };

    return (
        <div className={styles.container}>
            <div className={styles.header}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                    <h1 className={styles.title}>
                        {currentTag ? `标签: #${currentTag}` : '社区动态'}
                    </h1>
                    {currentTag && (
                        <button onClick={clearTag} style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#64748b' }}>
                            <X size={20} />
                        </button>
                    )}
                </div>
                <Link to="/social/create">
                    <Button variant="social">
                        <Plus size={20} style={{ marginRight: '0.5rem' }} />
                        发布帖子
                    </Button>
                </Link>
            </div>

            <div className={styles.feed}>
                {posts.map(post => (
                    <PostCard key={post.id} post={post} />
                ))}
            </div>

            {loading && <div className={styles.loading}>加载中...</div>}

            {!loading && hasMore && (
                <div className={styles.loadMore}>
                    <Button variant="secondary" onClick={handleLoadMore}>
                        加载更多
                    </Button>
                </div>
            )}

            {!loading && !hasMore && posts.length > 0 && (
                <div className={styles.endMessage}>到底啦！</div>
            )}

            {!loading && posts.length === 0 && (
                <div className={styles.endMessage}>
                    {currentTag ? '该标签下暂无帖子' : '还没有帖子，快来抢沙发！'}
                </div>
            )}
        </div>
    );
};

export default FeedPage;
