import { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { useNavigate, Link } from 'react-router-dom';
import Input from '../../components/Input';
import Button from '../../components/Button';
import Card from '../../components/Card';
import styles from './Auth.module.css';

const RegisterPage = () => {
    const [formData, setFormData] = useState({
        username: '',
        email: '',
        password: '',
        confirmPassword: '',
        role: 'user' // default role
    });
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const { register } = useAuth();
    const navigate = useNavigate();

    const handleChange = (e) => {
        setFormData(prev => ({ ...prev, [e.target.name]: e.target.value }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (formData.password !== formData.confirmPassword) {
            return setError("两次输入的密码不一致");
        }

        setError('');
        setLoading(true);

        try {
            // API expects: username, email, password, role
            await register({
                username: formData.username,
                email: formData.email,
                password: formData.password,
                role: formData.role
            });
            navigate('/social');
        } catch (err) {
            console.error('Registration failed', err);
            const errMsg = err.response?.data?.error || err.message || '注册失败，请重试。';
            setError(errMsg);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className={styles.container}>
            <Card className={styles.authCard} title="创建账号">
                <form onSubmit={handleSubmit} className={styles.form}>
                    <Input
                        label="用户名"
                        name="username"
                        type="text"
                        placeholder="请设置用户名"
                        value={formData.username}
                        onChange={handleChange}
                        required
                    />
                    <Input
                        label="邮箱"
                        name="email"
                        type="email"
                        placeholder="请输入邮箱"
                        value={formData.email}
                        onChange={handleChange}
                        required
                    />
                    <Input
                        label="密码"
                        name="password"
                        type="password"
                        placeholder="请设置密码"
                        value={formData.password}
                        onChange={handleChange}
                        required
                    />
                    <Input
                        label="确认密码"
                        name="confirmPassword"
                        type="password"
                        placeholder="请再次输入密码"
                        value={formData.confirmPassword}
                        onChange={handleChange}
                        required
                    />

                    {error && <div className={styles.error}>{error}</div>}

                    <Button type="submit" variant="primary" className={styles.submitBtn} disabled={loading}>
                        {loading ? '正在创建账号...' : '注册'}
                    </Button>

                    <div className={styles.footer}>
                        已有账号？ <Link to="/auth/login" className={styles.link}>立即登录</Link>
                    </div>
                </form>
            </Card>
        </div>
    );
};

export default RegisterPage;
