import React from 'react';
import styles from './AdminPage.module.css';
import { Edit2, Trash2 } from 'lucide-react';

const GenericTable = ({ columns, data, onEdit, onDelete }) => {
    return (
        <div className={styles.tableContainer}>
            <table className={styles.table}>
                <thead>
                    <tr>
                        {columns.map(col => (
                            <th key={col.key}>
                                {col.label}
                            </th>
                        ))}
                        <th>操作</th>
                    </tr>
                </thead>
                <tbody>
                    {data.length === 0 ? (
                        <tr>
                            <td colSpan={columns.length + 1} className={styles.emptyState}>
                                暂无数据
                            </td>
                        </tr>
                    ) : (
                        data.map(item => (
                            <tr key={item.id}>
                                {columns.map(col => (
                                    <td key={col.key}>
                                        {String(item[col.key] !== undefined && item[col.key] !== null ? item[col.key] : '')}
                                    </td>
                                ))}
                                <td>
                                    <button 
                                        onClick={() => onEdit(item)}
                                        className={`${styles.actionBtn} ${styles.editBtn}`}
                                        title="编辑"
                                    >
                                        <Edit2 size={16} />
                                    </button>
                                    <button 
                                        onClick={() => {
                                            if (window.confirm('确定要删除吗？')) {
                                                onDelete(item.id);
                                            }
                                        }}
                                        className={`${styles.actionBtn} ${styles.deleteBtn}`}
                                        title="删除"
                                    >
                                        <Trash2 size={16} />
                                    </button>
                                </td>
                            </tr>
                        ))
                    )}
                </tbody>
            </table>
        </div>
    );
};

export default GenericTable;
