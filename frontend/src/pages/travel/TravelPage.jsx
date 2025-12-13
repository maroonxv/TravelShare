import { useState } from 'react';
import MyTripsPage from './MyTripsPage';
import PublicTripsPage from './PublicTripsPage';
import styles from './TravelList.module.css';
import { Search } from 'lucide-react';

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
            <div className={styles.header}>
                <h1 className={styles.title}>旅行</h1>
                
                <div className={styles.tabs}>
                    <button 
                        onClick={() => setActiveTab('discover')}
                        className={`${styles.tab} ${activeTab === 'discover' ? styles.activeTab : ''}`}
                    >
                        发现
                    </button>
                    <button 
                        onClick={() => setActiveTab('my_trips')}
                        className={`${styles.tab} ${activeTab === 'my_trips' ? styles.activeTab : ''}`}
                    >
                        我的旅行
                    </button>
                </div>
            </div>

            {activeTab === 'discover' && (
                <div className={styles.searchContainer}>
                    <form onSubmit={handleSearch}>
                        <Search className={styles.searchIcon} size={18} />
                        <input 
                            type="text"
                            value={tempSearch}
                            onChange={(e) => setTempSearch(e.target.value)}
                            placeholder="搜索公开旅行..."
                            className={styles.searchInput}
                        />
                    </form>
                </div>
            )}

            {activeTab === 'discover' ? (
                <div>
                    <PublicTripsPage searchQuery={searchQuery} />
                </div>
            ) : (
                <div>
                    <MyTripsPage />
                </div>
            )}
        </div>
    );
};

export default TravelPage;
