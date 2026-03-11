import styles from './Input.module.css';

const Input = ({ label, error, className = '', icon, id, ...props }) => {
    const inputId = id || props.name || label;

    return (
        <div className={`${styles.wrapper} ${className}`}>
            {label && (
                <label className={styles.label} htmlFor={inputId}>
                    {label}
                </label>
            )}
            <div className={styles.field}>
                {icon && <span className={styles.icon}>{icon}</span>}
                <input
                    id={inputId}
                    className={`${styles.input} ${icon ? styles.withIcon : ''} ${error ? styles.errorInput : ''}`}
                    {...props}
                />
            </div>
            {error && <span className={styles.errorMessage}>{error}</span>}
        </div>
    );
};

export default Input;
