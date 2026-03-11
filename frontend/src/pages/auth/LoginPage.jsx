import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/useAuth';
import Input from '../../components/Input';
import Button from '../../components/Button';
import Card from '../../components/Card';
import LoadingSpinner from '../../components/LoadingSpinner';
import { toast } from 'react-hot-toast';
import styles from './Auth.module.css';

const LoginPage = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const { login } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);
        try {
            await login(email, password);
            toast.success('登录成功');
            navigate('/social');
        } catch (err) {
            console.error('Login failed', err);
            const errMsg = err.response?.data?.error || err.message || '登录失败，请检查邮箱和密码。';
            setError(errMsg);
            toast.error(errMsg);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className={styles.container}>
            <div className={styles.authLayout}>
                <section className={styles.infoPanel}>
                    <div className={styles.brand}>TravelShare</div>
                    <div className={styles.heroBlock}>
                        <h1 className={styles.heroTitle}>把旅行计划、动态分享和朋友协作放到同一张工作台。</h1>
                        <p className={styles.heroText}>
                            登录后可以继续管理行程、发布旅行见闻、查看消息与好友互动，不用在多个页面之间来回切换。
                        </p>
                    </div>
                    <div className={styles.featureGrid}>
                        <div className={styles.featureCard}>
                            <span>社区</span>
                            <strong>照片、标签和旅行故事集中发布</strong>
                        </div>
                        <div className={styles.featureCard}>
                            <span>行程</span>
                            <strong>多人协作安排路线、预算和活动</strong>
                        </div>
                        <div className={styles.featureCard}>
                            <span>消息</span>
                            <strong>和好友、群组以及 AI 助手保持沟通</strong>
                        </div>
                    </div>
                </section>

                <Card className={styles.authCard}>
                    <div className={styles.formHeader}>
                        <h2>登录</h2>
                        <p>使用邮箱和密码继续。</p>
                    </div>

                    <form onSubmit={handleSubmit} className={styles.form}>
                        <Input
                            label="邮箱"
                            type="email"
                            placeholder="name@example.com"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                        />
                        <Input
                            label="密码"
                            type="password"
                            placeholder="输入你的登录密码"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                        />

                        {error && <div className={styles.error}>{error}</div>}

                        <Button type="submit" variant="primary" className={styles.submitBtn} disabled={loading}>
                            {loading ? (
                                <span className={styles.loadingRow}>
                                    <LoadingSpinner size="small" />
                                    <span>登录中...</span>
                                </span>
                            ) : (
                                '登录'
                            )}
                        </Button>

                        <div className={styles.footer}>
                            还没有账号？ <Link to="/auth/register" className={styles.link}>立即注册</Link>
                        </div>
                    </form>
                </Card>
            </div>
        </div>
    );
};

export default LoginPage;
