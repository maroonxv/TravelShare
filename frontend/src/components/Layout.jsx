import { Link, NavLink, Outlet, useLocation } from 'react-router-dom';
import { Bot, Globe, LogOut, Map, MessageSquare, Settings2, User } from 'lucide-react';
import { useAuth } from '../context/useAuth';
import styles from './Layout.module.css';

const navItems = [
    {
        to: '/social',
        label: '社区',
        description: '浏览旅行动态与分享',
        icon: Globe,
        accentClass: styles.social,
    },
    {
        to: '/travel',
        label: '行程',
        description: '创建、查看和协作规划',
        icon: Map,
        accentClass: styles.travel,
    },
    {
        to: '/chat',
        label: '消息',
        description: '和朋友或群组保持沟通',
        icon: MessageSquare,
        accentClass: styles.chat,
    },
    {
        to: '/ai-assistant',
        label: 'TripMateAI',
        description: '旅行问答、方案建议与检索',
        icon: Bot,
        accentClass: styles.ai,
    },
];

const pageMeta = [
    { match: '/social/create', title: '发布动态', description: '整理照片、标签和行程关联后再发布。' },
    { match: '/social/post', title: '帖子详情', description: '查看正文、评论和分享记录。' },
    { match: '/social', title: '社区', description: '集中查看大家的旅行动态、标签和最新内容。' },
    { match: '/travel/my-trips', title: '我的行程', description: '管理你参与和创建的旅行计划。' },
    { match: '/travel/public', title: '公开行程', description: '发现可浏览的公共路线和计划。' },
    { match: '/travel', title: '行程', description: '在发现与管理之间切换你的旅行工作台。' },
    { match: '/chat', title: '消息', description: '发起私聊、群聊并处理好友请求。' },
    { match: '/ai-assistant', title: 'TripMateAI', description: '围绕行程、景点和问题进行连续对话。' },
    { match: '/profile/edit', title: '资料设置', description: '更新头像、简介、位置和账户安全。' },
    { match: '/profile', title: '个人主页', description: '查看个人信息、动态和旅行记录。' },
];

const Layout = () => {
    const { user, logout } = useAuth();
    const location = useLocation();

    const currentMeta =
        pageMeta.find((item) => location.pathname.startsWith(item.match)) || pageMeta[0];

    return (
        <div className={styles.shell}>
            <aside className={styles.sidebar}>
                <div className={styles.brandBlock}>
                    <Link className={styles.brand} to="/social">
                        <span className={styles.brandMark}>TS</span>
                        <span className={styles.brandText}>
                            <strong>TravelShare</strong>
                            <span>旅行社交与协作</span>
                        </span>
                    </Link>
                </div>

                <nav className={styles.nav}>
                    {navItems.map((item) => {
                        const Icon = item.icon;
                        return (
                            <NavLink
                                key={item.to}
                                to={item.to}
                                className={({ isActive }) =>
                                    [styles.link, item.accentClass, isActive ? styles.active : '']
                                        .filter(Boolean)
                                        .join(' ')
                                }
                            >
                                <span className={styles.linkIcon}>
                                    <Icon size={18} />
                                </span>
                                <span className={styles.linkBody}>
                                    <span className={styles.linkLabel}>{item.label}</span>
                                    <span className={styles.linkHint}>{item.description}</span>
                                </span>
                            </NavLink>
                        );
                    })}
                </nav>

                <div className={styles.sidebarFooter}>
                    <Link className={styles.profileCard} to={`/profile/${user?.id || ''}`}>
                        <span className={styles.profileAvatar}>
                            {user?.profile?.avatar_url ? (
                                <img alt={user?.username || 'avatar'} src={user.profile.avatar_url} />
                            ) : (
                                (user?.username || 'U').charAt(0).toUpperCase()
                            )}
                        </span>
                        <span className={styles.profileBody}>
                            <span className={styles.profileName}>{user?.username || 'Traveler'}</span>
                            <span className={styles.profileRole}>{user?.role === 'admin' ? '管理员' : '普通用户'}</span>
                        </span>
                    </Link>

                    {user?.role === 'admin' && (
                        <Link className={styles.adminLink} to="/admin/users">
                            <Settings2 size={16} />
                            <span>进入后台</span>
                        </Link>
                    )}

                    <button className={styles.logoutBtn} onClick={logout} type="button">
                        <LogOut size={16} />
                        <span>退出登录</span>
                    </button>
                </div>
            </aside>

            <div className={styles.viewport}>
                <header className={styles.topbar}>
                    <div className={styles.pageMeta}>
                        <h1>{currentMeta.title}</h1>
                        <p>{currentMeta.description}</p>
                    </div>
                    <Link className={styles.topbarProfile} to={`/profile/${user?.id || ''}`}>
                        <User size={16} />
                        <span>{user?.username || 'Traveler'}</span>
                    </Link>
                </header>

                <nav className={styles.mobileNav}>
                    {navItems.map((item) => {
                        const Icon = item.icon;
                        return (
                            <NavLink
                                key={item.to}
                                to={item.to}
                                className={({ isActive }) =>
                                    [styles.mobileLink, isActive ? styles.mobileActive : '']
                                        .filter(Boolean)
                                        .join(' ')
                                }
                            >
                                <Icon size={16} />
                                <span>{item.label}</span>
                            </NavLink>
                        );
                    })}
                </nav>

                <main className={styles.main}>
                    <div className={styles.content}>
                        <Outlet />
                    </div>
                </main>
            </div>
        </div>
    );
};

export default Layout;
