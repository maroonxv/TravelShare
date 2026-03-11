import { useEffect, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { Plus, Search, X } from 'lucide-react';
import { getFeed } from '../../api/social';
import PostCard from '../../components/PostCard';
import Button from '../../components/Button';
import LoadingSpinner from '../../components/LoadingSpinner';
import { toast } from 'react-hot-toast';
import styles from './FeedPage.module.css';

const FeedPage = () => {
    const [searchParams, setSearchParams] = useSearchParams();
    const currentTag = searchParams.get('tag');
    const currentSearch = searchParams.get('search') || '';
    const [tempSearch, setTempSearch] = useState(currentSearch);
    const [activeTab, setActiveTab] = useState('recommend');
    const [posts, setPosts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [offset, setOffset] = useState(0);
    const [hasMore, setHasMore] = useState(true);
    const LIMIT = 10;

    useEffect(() => {
        setTempSearch(currentSearch);
    }, [currentSearch]);

    useEffect(() => {
        const loadInitial = async () => {
            setLoading(true);
            try {
                const tags = currentTag ? [currentTag] : [];
                const data = await getFeed(LIMIT, 0, tags, currentSearch);
                const nextPosts = Array.isArray(data) ? data : data.posts || [];
                setPosts(nextPosts);
                setOffset(LIMIT);
                setHasMore(nextPosts.length === LIMIT);
            } catch (error) {
                console.error('Failed to fetch feed', error);
                toast.error('获取动态失败');
            } finally {
                setLoading(false);
            }
        };

        loadInitial();
    }, [currentTag, currentSearch, activeTab]);

    const handleLoadMore = async () => {
        if (loading) return;
        setLoading(true);
        try {
            const tags = currentTag ? [currentTag] : [];
            const data = await getFeed(LIMIT, offset, tags, currentSearch);
            const nextPosts = Array.isArray(data) ? data : data.posts || [];

            setPosts((prev) => {
                const existingIds = new Set(prev.map((post) => post.id));
                const uniqueNewPosts = nextPosts.filter((post) => !existingIds.has(post.id));
                return [...prev, ...uniqueNewPosts];
            });
            setOffset((prev) => prev + LIMIT);
            setHasMore(nextPosts.length === LIMIT);
        } catch (error) {
            console.error('Failed to fetch more posts', error);
            toast.error('加载更多失败');
        } finally {
            setLoading(false);
        }
    };

    const handleSearch = (e) => {
        e.preventDefault();
        setSearchParams((prev) => {
            const nextParams = new URLSearchParams(prev);
            if (tempSearch) {
                nextParams.set('search', tempSearch);
            } else {
                nextParams.delete('search');
            }
            return nextParams;
        });
    };

    const clearTag = () => {
        setSearchParams((prev) => {
            const nextParams = new URLSearchParams(prev);
            nextParams.delete('tag');
            return nextParams;
        });
    };

    const headerTitle = currentTag ? `标签 #${currentTag}` : currentSearch ? '搜索结果' : '社区动态';
    const headerDescription = currentTag
        ? '查看同一标签下的旅行内容。'
        : currentSearch
          ? `关键词“${currentSearch}”相关的内容。`
          : '按推荐、最新和热门浏览大家的旅行分享。';

    return (
        <div className={styles.container}>
            <header className={styles.header}>
                <div className={styles.titleRow}>
                    <div className={styles.titleBlock}>
                        <h1 className={styles.title}>{headerTitle}</h1>
                        <p className={styles.subtitle}>{headerDescription}</p>
                    </div>

                    <Link to="/social/create">
                        <Button icon={<Plus size={16} />} variant="social">
                            发布动态
                        </Button>
                    </Link>
                </div>

                <div className={styles.toolsRow}>
                    <form onSubmit={handleSearch} className={styles.searchForm}>
                        <Search size={16} className={styles.searchIcon} />
                        <input
                            type="text"
                            value={tempSearch}
                            onChange={(e) => setTempSearch(e.target.value)}
                            placeholder="搜索标题、内容或标签"
                            className={styles.searchInput}
                        />
                    </form>

                    {currentTag && (
                        <button onClick={clearTag} className={styles.clearBtn} type="button">
                            <X size={16} />
                            <span>清除标签</span>
                        </button>
                    )}
                </div>

                {!currentTag && !currentSearch && (
                    <div className={styles.filterTabs}>
                        <button
                            className={`${styles.filterTab} ${activeTab === 'recommend' ? styles.activeTab : ''}`}
                            onClick={() => setActiveTab('recommend')}
                            type="button"
                        >
                            推荐
                        </button>
                        <button
                            className={`${styles.filterTab} ${activeTab === 'latest' ? styles.activeTab : ''}`}
                            onClick={() => setActiveTab('latest')}
                            type="button"
                        >
                            最新
                        </button>
                        <button
                            className={`${styles.filterTab} ${activeTab === 'hot' ? styles.activeTab : ''}`}
                            onClick={() => setActiveTab('hot')}
                            type="button"
                        >
                            热门
                        </button>
                    </div>
                )}
            </header>

            <div className={styles.feed}>
                {posts.map((post) => (
                    <PostCard key={post.id} post={post} />
                ))}
            </div>

            {loading && (
                <div className={styles.loading}>
                    <LoadingSpinner size="medium" />
                </div>
            )}

            {!loading && hasMore && (
                <div className={styles.loadMore}>
                    <Button variant="secondary" onClick={handleLoadMore}>
                        加载更多
                    </Button>
                </div>
            )}

            {!loading && !hasMore && posts.length > 0 && <div className={styles.endMessage}>已经到底了</div>}

            {!loading && posts.length === 0 && (
                <div className={styles.endMessage}>
                    {currentTag ? '这个标签下还没有内容。' : '暂时还没有可展示的动态。'}
                </div>
            )}
        </div>
    );
};

export default FeedPage;
