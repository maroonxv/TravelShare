import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { createPost } from '../../api/social';
import { getUserTrips } from '../../api/travel';
import Button from '../../components/Button';
import Input from '../../components/Input';
import Card from '../../components/Card';
import { Image as ImageIcon, MapPin, X } from 'lucide-react';
import styles from './CreatePostPage.module.css';

const CreatePostPage = () => {
    const { user } = useAuth();
    const navigate = useNavigate();
    const [title, setTitle] = useState('');
    const [content, setContent] = useState('');
    const [tags, setTags] = useState('');
    const [selectedTrip, setSelectedTrip] = useState('');
    const [visibility, setVisibility] = useState('public');
    const [images, setImages] = useState([]);
    const [previews, setPreviews] = useState([]);
    const [myTrips, setMyTrips] = useState([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (user) {
            fetchTrips();
        }
        return () => {
            previews.forEach(url => URL.revokeObjectURL(url));
        };
    }, [user]);

    const fetchTrips = async () => {
        try {
            const trips = await getUserTrips(user.id);
            setMyTrips(Array.isArray(trips) ? trips : (trips.trips || []));
        } catch (error) {
            console.error("Failed to load trips", error);
        }
    };

    const handleImageChange = (e) => {
        const files = Array.from(e.target.files);
        if (files.length > 0) {
            setImages(prev => [...prev, ...files]);
            const newPreviews = files.map(file => URL.createObjectURL(file));
            setPreviews(prev => [...prev, ...newPreviews]);
        }
    };

    const removeImage = (index) => {
        setImages(prev => prev.filter((_, i) => i !== index));
        setPreviews(prev => {
            const newPreviews = [...prev];
            URL.revokeObjectURL(newPreviews[index]);
            newPreviews.splice(index, 1);
            return newPreviews;
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
        
        images.forEach(image => {
            formData.append('media_files', image);
        });

        try {
            await createPost(formData);
            navigate('/social');
        } catch (error) {
            console.error("Failed to create post", error);
            alert("发布帖子失败");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className={styles.container}>
            <Card className={styles.formCard} title="发布新帖子">
                <form onSubmit={handleSubmit} className={styles.form}>
                    <Input
                        label="标题"
                        placeholder="给你的帖子起个标题吧"
                        value={title}
                        onChange={(e) => setTitle(e.target.value)}
                        required
                    />

                    <div className={styles.textareaWrapper}>
                        <label className={styles.label}>内容</label>
                        <textarea
                            className={styles.textarea}
                            placeholder="分享你的旅行经历..."
                            value={content}
                            onChange={(e) => setContent(e.target.value)}
                            required
                        />
                    </div>

                    {previews.length > 0 && (
                        <div className={styles.imagePreviewGrid} style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(100px, 1fr))', gap: '10px', marginBottom: '20px' }}>
                            {previews.map((url, index) => (
                                <div key={index} style={{ position: 'relative', aspectRatio: '1/1' }}>
                                    <img src={url} alt={`Preview ${index}`} style={{ width: '100%', height: '100%', objectFit: 'cover', borderRadius: '8px' }} />
                                    <button 
                                        type="button" 
                                        onClick={() => removeImage(index)}
                                        style={{ 
                                            position: 'absolute', top: -5, right: -5, 
                                            background: 'red', color: 'white', 
                                            border: 'none', borderRadius: '50%', 
                                            width: '20px', height: '20px', 
                                            display: 'flex', alignItems: 'center', justifyContent: 'center',
                                            cursor: 'pointer'
                                        }}
                                    >
                                        <X size={12} />
                                    </button>
                                </div>
                            ))}
                        </div>
                    )}

                    <div className={styles.uploadArea}>
                        <label htmlFor="image-upload" className={styles.uploadLabel}>
                            <ImageIcon size={24} />
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
                            <label className={styles.label}>关联旅行 (可选)</label>
                            <div className={styles.selectContainer}>
                                <MapPin size={16} className={styles.selectIcon} />
                                <select
                                    className={styles.select}
                                    value={selectedTrip}
                                    onChange={(e) => setSelectedTrip(e.target.value)}
                                >
                                    <option value="">选择一个旅行...</option>
                                    {myTrips.map(trip => (
                                        <option key={trip.id} value={trip.id}>{trip.name}</option>
                                    ))}
                                </select>
                            </div>
                        </div>

                        <Input
                            label="标签 (逗号分隔)"
                            placeholder="travel, fun, japan"
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
                            {loading ? '发布中...' : '发布'}
                        </Button>
                    </div>
                </form>
            </Card>
        </div>
    );
};

export default CreatePostPage;
