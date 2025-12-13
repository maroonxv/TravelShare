import styles from './LoadingSpinner.module.css';

const LoadingSpinner = ({ size = 'medium', className = '' }) => {
    return (
        <div className={`${styles.container} ${className}`}>
            <div className={`${styles.spinner} ${styles[size]}`} />
        </div>
    );
};

export default LoadingSpinner;
