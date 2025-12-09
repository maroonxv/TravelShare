import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Plus } from 'lucide-react';
import { getFeed } from '../../api/social';
import PostCard from '../../components/PostCard';
import Button from '../../components/Button';
import styles from './FeedPage.module.css';

const FeedPage = () => {
    const [posts, setPosts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [offset, setOffset] = useState(0);
    const [hasMore, setHasMore] = useState(true);
    const LIMIT = 10;

    useEffect(() => {
        fetchPosts();
    }, []);

    const fetchPosts = async () => {
        try {
            const data = await getFeed(LIMIT, offset);
            // Assuming api returns { posts: [...], total: ... } or just array
            // Let's assume list for now based on prompt "Returns a list of posts"

            const newPosts = Array.isArray(data) ? data : (data.posts || []);

            setPosts(prev => [...prev, ...newPosts]);
            setOffset(prev => prev + LIMIT);

            if (newPosts.length < LIMIT) {
                setHasMore(false);
            }
        } catch (error) {
            console.error('Failed to fetch feed', error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className={styles.container}>
            <div className={styles.header}>
                <h1 className={styles.title}>Social Feed</h1>
                <Link to="/social/create">
                    <Button variant="social">
                        <Plus size={20} style={{ marginRight: '0.5rem' }} />
                        Create Post
                    </Button>
                </Link>
            </div>

            <div className={styles.feed}>
                {posts.map(post => (
                    <PostCard key={post.id} post={post} />
                ))}
            </div>

            {loading && <div className={styles.loading}>Loading feed...</div>}

            {!loading && hasMore && (
                <div className={styles.loadMore}>
                    <Button variant="secondary" onClick={fetchPosts}>
                        Load More
                    </Button>
                </div>
            )}

            {!loading && !hasMore && posts.length > 0 && (
                <div className={styles.endMessage}>You've reached the end!</div>
            )}

            {!loading && posts.length === 0 && (
                <div className={styles.endMessage}>No posts yet. Be the first to share!</div>
            )}
        </div>
    );
};

export default FeedPage;
