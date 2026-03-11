import styles from './Button.module.css';

const Button = ({
    children,
    variant = 'primary',
    className = '',
    icon,
    iconPosition = 'start',
    fullWidth = false,
    ...props
}) => {
    const iconMarkup = icon ? <span className={styles.icon}>{icon}</span> : null;

    return (
        <button
            className={[
                styles.button,
                styles[variant] || styles.primary,
                fullWidth ? styles.fullWidth : '',
                className,
            ]
                .filter(Boolean)
                .join(' ')}
            {...props}
        >
            {iconPosition === 'start' && iconMarkup}
            <span className={styles.label}>{children}</span>
            {iconPosition === 'end' && iconMarkup}
        </button>
    );
};

export default Button;
