import React from 'react';
import { Link, Outlet, useLocation } from 'react-router-dom';
import { resources } from '../config/resources';
import { useAuth } from '../../context/AuthContext';
import styles from './AdminLayout.module.css';
import { 
    Users, Map, FileText, MessageSquare, Heart, 
    MessageCircle, Mail, Activity, LayoutGrid, ArrowLeft 
} from 'lucide-react';

const iconMap = {
    users: Users,
    trips: Map,
    posts: FileText,
    comments: MessageSquare,
    likes: Heart,
    conversations: MessageCircle,
    messages: Mail,
    activities: Activity
};

const AdminLayout = () => {
    const { user } = useAuth();
    const location = useLocation();

    if (!user || user.role !== 'admin') {
        return <div className={styles.accessDenied}>Access Denied: Admin only.</div>;
    }

    return (
        <div className={styles.container}>
            <aside className={styles.sidebar}>
                <div className={styles.logo}>Admin</div>
                <nav className={styles.nav}>
                    {Object.keys(resources).map(key => {
                        const Icon = iconMap[key] || LayoutGrid;
                        return (
                            <Link 
                                key={key} 
                                to={`/admin/${key}`}
                                className={`${styles.link} ${location.pathname.includes(`/admin/${key}`) ? styles.active : ''}`}
                            >
                                <Icon size={20} />
                                <span>{resources[key].label}</span>
                            </Link>
                        );
                    })}
                </nav>
                <div className={styles.footer}>
                    <Link to="/" className={styles.backBtn}>
                        <ArrowLeft size={20} />
                        <span>返回前台</span>
                    </Link>
                </div>
            </aside>
            <main className={styles.main}>
                <Outlet />
            </main>
        </div>
    );
};

export default AdminLayout;
