import { useCallback, useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Image as ImageIcon, MapPin, X } from 'lucide-react';
import { toast } from 'react-hot-toast';
import { createPost } from '../../api/social';
import { getUserTrips } from '../../api/travel';
import { useAuth } from '../../context/useAuth';
import Button from '../../components/Button';
import Card from '../../components/Card';
import Input from '../../components/Input';
import LoadingSpinner from '../../components/LoadingSpinner';
import styles from './CreatePostPage.module.css';

const CreatePostPage = () => {
    const { user } = useAuth();
    const navigate = useNavigate();
    const [title, setTitle] = useState('');
    const [content, setContent] = useState('');
    const [tags, setTags] = useState('');
    const [selectedTrip, setSelectedTrip] = useState('');
    const [visibility] = useState('public');
    const [images, setImages] = useState([]);
    const [previews, setPreviews] = useState([]);
    const [myTrips, setMyTrips] = useState([]);
    const [loading, setLoading] = useState(false);
    const previewsRef = useRef(previews);

    useEffect(() => {
        previewsRef.current = previews;
    }, [previews]);

    const fetchTrips = useCallback(async () => {
        if (!user?.id) return;
        try {
            const trips = await getUserTrips(user.id);
            setMyTrips(Array.isArray(trips) ? trips : trips.trips || []);
        } catch (error) {
            console.error('Failed to load trips', error);
            toast.error('加载行程列表失败');
        }
    }, [user?.id]);

    useEffect(() => {
        if (user) fetchTrips();
        return () => {
            previewsRef.current.forEach((url) => URL.revokeObjectURL(url));
        };
    }, [fetchTrips, user]);

    const handleImageChange = (e) => {
        const files = Array.from(e.target.files);
        if (files.length === 0) return;

        setImages((prev) => [...prev, ...files]);
        const newPreviews = files.map((file) => URL.createObjectURL(file));
        setPreviews((prev) => [...prev, ...newPreviews]);
    };

    const removeImage = (index) => {
        setImages((prev) => prev.filter((_, i) => i !== index));
        setPreviews((prev) => {
            const nextPreviews = [...prev];
            URL.revokeObjectURL(nextPreviews[index]);
            nextPreviews.splice(index, 1);
            return nextPreviews;
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);

        const formData = new FormData();
        formData.append('title', title);
        formData.append('content', content);
        formData.append('tags', tags);
        formData.append('visibility', visibility);
        if (selectedTrip) formData.append('trip_id', selectedTrip);
        images.forEach((image) => {
            formData.append('media_files', image);
        });

        try {
            await createPost(formData);
            toast.success('动态发布成功');
            navigate('/social');
        } catch (error) {
            console.error('Failed to create post', error);
            toast.error('发布动态失败');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className={styles.container}>
            <Card className={styles.formCard}>
                <div className={styles.header}>
                    <div>
                        <h1 className={styles.title}>发布新动态</h1>
                        <p className={styles.subtitle}>整理标题、正文、图片和关联行程，让内容更完整也更容易被找到。</p>
                    </div>
                </div>

                <form onSubmit={handleSubmit} className={styles.form}>
                    <Input
                        label="标题"
                        placeholder="给这次分享起一个清晰的标题"
                        value={title}
                        onChange={(e) => setTitle(e.target.value)}
                        required
                    />

                    <div className={styles.textareaWrapper}>
                        <label className={styles.label}>内容</label>
                        <textarea
                            className={styles.textarea}
                            placeholder="记录行程亮点、经验、照片背景或推荐理由"
                            value={content}
                            onChange={(e) => setContent(e.target.value)}
                            required
                        />
                    </div>

                    {previews.length > 0 && (
                        <div className={styles.imagePreviewGrid}>
                            {previews.map((url, index) => (
                                <div key={index} className={styles.imagePreviewItem}>
                                    <img src={url} alt={`Preview ${index + 1}`} className={styles.previewImage} />
                                    <button type="button" onClick={() => removeImage(index)} className={styles.removeImageBtn}>
                                        <X size={12} />
                                    </button>
                                </div>
                            ))}
                        </div>
                    )}

                    <div className={styles.uploadArea}>
                        <label htmlFor="image-upload" className={styles.uploadLabel}>
                            <ImageIcon size={22} />
                            <span>添加照片</span>
                        </label>
                        <input
                            id="image-upload"
                            type="file"
                            accept="image/*"
                            onChange={handleImageChange}
                            multiple
                            style={{ display: 'none' }}
                        />
                    </div>

                    <div className={styles.row}>
                        <div className={styles.selectWrapper}>
                            <label className={styles.label}>关联行程</label>
                            <div className={styles.selectContainer}>
                                <MapPin size={16} className={styles.selectIcon} />
                                <select className={styles.select} value={selectedTrip} onChange={(e) => setSelectedTrip(e.target.value)}>
                                    <option value="">不关联具体行程</option>
                                    {myTrips.map((trip) => (
                                        <option key={trip.id} value={trip.id}>
                                            {trip.name}
                                        </option>
                                    ))}
                                </select>
                            </div>
                        </div>

                        <Input
                            label="标签"
                            placeholder="例如：海边, 徒步, 美食"
                            value={tags}
                            onChange={(e) => setTags(e.target.value)}
                            className={styles.tagsInput}
                        />
                    </div>

                    <div className={styles.actions}>
                        <Button type="button" variant="secondary" onClick={() => navigate('/social')}>
                            取消
                        </Button>
                        <Button type="submit" variant="social" disabled={loading}>
                            {loading ? (
                                <span className={styles.loadingRow}>
                                    <LoadingSpinner size="small" />
                                    <span>发布中...</span>
                                </span>
                            ) : (
                                '发布动态'
                            )}
                        </Button>
                    </div>
                </form>
            </Card>
        </div>
    );
};

export default CreatePostPage;
