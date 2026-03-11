import { useState } from 'react';
import { Search } from 'lucide-react';
import MyTripsPage from './MyTripsPage';
import PublicTripsPage from './PublicTripsPage';
import styles from './TravelList.module.css';

const TravelPage = () => {
    const [activeTab, setActiveTab] = useState('discover');
    const [searchQuery, setSearchQuery] = useState('');
    const [tempSearch, setTempSearch] = useState('');

    const handleSearch = (e) => {
        e.preventDefault();
        setSearchQuery(tempSearch);
    };

    return (
        <div className={styles.container}>
            <header className={styles.header}>
                <div className={styles.titleBlock}>
                    <h1 className={styles.title}>行程规划</h1>
                    <p className={styles.subtitle}>在公开路线和我的行程之间切换，保持计划与协作都清晰可见。</p>
                </div>

                <div className={styles.tabs}>
                    <button
                        onClick={() => setActiveTab('discover')}
                        className={`${styles.tab} ${activeTab === 'discover' ? styles.activeTab : ''}`}
                        type="button"
                    >
                        发现路线
                    </button>
                    <button
                        onClick={() => setActiveTab('my_trips')}
                        className={`${styles.tab} ${activeTab === 'my_trips' ? styles.activeTab : ''}`}
                        type="button"
                    >
                        我的行程
                    </button>
                </div>
            </header>

            {activeTab === 'discover' && (
                <div className={styles.searchContainer}>
                    <form onSubmit={handleSearch} className={styles.searchForm}>
                        <Search className={styles.searchIcon} size={18} />
                        <input
                            type="text"
                            value={tempSearch}
                            onChange={(e) => setTempSearch(e.target.value)}
                            placeholder="搜索公开行程、地点或主题"
                            className={styles.searchInput}
                        />
                    </form>
                </div>
            )}

            {activeTab === 'discover' ? <PublicTripsPage searchQuery={searchQuery} /> : <MyTripsPage />}
        </div>
    );
};

export default TravelPage;
