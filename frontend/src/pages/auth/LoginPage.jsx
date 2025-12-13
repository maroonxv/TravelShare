import { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { useNavigate, Link } from 'react-router-dom';
import Input from '../../components/Input';
import Button from '../../components/Button';
import Card from '../../components/Card';
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
            navigate('/social');
        } catch (err) {
            console.error('Login failed', err);
            const errMsg = err.response?.data?.error || err.message || '登录失败，请检查您的凭证。';
            setError(errMsg);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className={styles.container}>
            <Card className={styles.authCard} title="欢迎回来">
                <form onSubmit={handleSubmit} className={styles.form}>
                    <Input
                        label="邮箱"
                        type="email"
                        placeholder="请输入邮箱"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                    />
                    <Input
                        label="密码"
                        type="password"
                        placeholder="请输入密码"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                    />
                    {error && <div className={styles.error}>{error}</div>}

                    <Button type="submit" variant="primary" className={styles.submitBtn} disabled={loading}>
                        {loading ? '登录中...' : '登录'}
                    </Button>

                    <div className={styles.footer}>
                        还没有账号？ <Link to="/auth/register" className={styles.link}>立即注册</Link>
                    </div>
                </form>
            </Card>
        </div>
    );
};

export default LoginPage;
