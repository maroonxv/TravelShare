import { useState } from 'react';
import styles from './AdminPage.module.css';

const GenericForm = ({ fields, initialData, onSubmit, onCancel }) => {
    const [formData, setFormData] = useState(() => initialData || {});

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        onSubmit(formData);
    };

    return (
        <div className={styles.modalOverlay}>
            <div className={styles.modalContent}>
                <h3 className={styles.modalTitle}>{initialData ? '编辑' : '新建'}</h3>
                <form onSubmit={handleSubmit}>
                    {fields.map(field => (
                        <div key={field.name} className={styles.formGroup}>
                            <label className={styles.label}>
                                {field.label} {field.required && <span className={styles.required}>*</span>}
                            </label>
                            {field.type === 'select' ? (
                                <select
                                    name={field.name}
                                    value={formData[field.name] || ''}
                                    onChange={handleChange}
                                    className={styles.select}
                                    required={field.required}
                                >
                                    <option value="">请选择</option>
                                    {field.options.map(opt => (
                                        <option key={opt} value={opt}>{opt}</option>
                                    ))}
                                </select>
                            ) : field.type === 'textarea' ? (
                                <textarea
                                    name={field.name}
                                    value={formData[field.name] || ''}
                                    onChange={handleChange}
                                    className={styles.textarea}
                                    required={field.required}
                                />
                            ) : (
                                <input
                                    type={field.type || 'text'}
                                    name={field.name}
                                    value={formData[field.name] || ''}
                                    onChange={handleChange}
                                    className={styles.input}
                                    required={field.required}
                                />
                            )}
                        </div>
                    ))}
                    <div className={styles.buttonGroup}>
                        <button type="button" onClick={onCancel} className={styles.cancelBtn}>取消</button>
                        <button type="submit" className={styles.saveBtn}>保存</button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default GenericForm;
