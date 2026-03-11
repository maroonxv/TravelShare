import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/useAuth';
import Input from '../../components/Input';
import Button from '../../components/Button';
import Card from '../../components/Card';
import LoadingSpinner from '../../components/LoadingSpinner';
import { toast } from 'react-hot-toast';
import styles from './Auth.module.css';

const RegisterPage = () => {
    const [formData, setFormData] = useState({
        username: '',
        email: '',
        password: '',
        confirmPassword: '',
        role: 'user',
    });
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const { register } = useAuth();
    const navigate = useNavigate();

    const handleChange = (e) => {
        setFormData((prev) => ({ ...prev, [e.target.name]: e.target.value }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (formData.password !== formData.confirmPassword) {
            const msg = '两次输入的密码不一致。';
            setError(msg);
            toast.error(msg);
            return;
        }

        setError('');
        setLoading(true);

        try {
            await register({
                username: formData.username,
                email: formData.email,
                password: formData.password,
                role: formData.role,
            });
            toast.success('注册成功');
            navigate('/social');
        } catch (err) {
            console.error('Registration failed', err);
            const errMsg = err.response?.data?.error || err.message || '注册失败，请稍后重试。';
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
                        <h1 className={styles.heroTitle}>开始建立自己的旅行档案、路线协作和社交关系。</h1>
                        <p className={styles.heroText}>
                            注册后可以发布内容、加入好友、参与群聊，并把每一次出发都沉淀成可复用的计划。
                        </p>
                    </div>
                    <div className={styles.featureGrid}>
                        <div className={styles.featureCard}>
                            <span>计划</span>
                            <strong>把预算、成员和每日活动整理在同一处</strong>
                        </div>
                        <div className={styles.featureCard}>
                            <span>记录</span>
                            <strong>随时把照片、地点和标签整理成动态</strong>
                        </div>
                        <div className={styles.featureCard}>
                            <span>协作</span>
                            <strong>邀请好友、群聊沟通并持续迭代路线</strong>
                        </div>
                    </div>
                </section>

                <Card className={styles.authCard}>
                    <div className={styles.formHeader}>
                        <h2>创建账号</h2>
                        <p>填写基本信息后即可开始使用。</p>
                    </div>

                    <form onSubmit={handleSubmit} className={styles.form}>
                        <Input
                            label="用户名"
                            name="username"
                            type="text"
                            placeholder="例如：山野旅人"
                            value={formData.username}
                            onChange={handleChange}
                            required
                        />
                        <Input
                            label="邮箱"
                            name="email"
                            type="email"
                            placeholder="name@example.com"
                            value={formData.email}
                            onChange={handleChange}
                            required
                        />
                        <Input
                            label="密码"
                            name="password"
                            type="password"
                            placeholder="设置登录密码"
                            value={formData.password}
                            onChange={handleChange}
                            required
                        />
                        <Input
                            label="确认密码"
                            name="confirmPassword"
                            type="password"
                            placeholder="再次输入密码"
                            value={formData.confirmPassword}
                            onChange={handleChange}
                            required
                        />

                        {error && <div className={styles.error}>{error}</div>}

                        <Button type="submit" variant="primary" className={styles.submitBtn} disabled={loading}>
                            {loading ? (
                                <span className={styles.loadingRow}>
                                    <LoadingSpinner size="small" />
                                    <span>注册中...</span>
                                </span>
                            ) : (
                                '注册'
                            )}
                        </Button>

                        <div className={styles.footer}>
                            已有账号？ <Link to="/auth/login" className={styles.link}>立即登录</Link>
                        </div>
                    </form>
                </Card>
            </div>
        </div>
    );
};

export default RegisterPage;
