import React, { useState, useEffect, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import { resources } from '../config/resources';
import * as api from '../../api/admin';
import GenericTable from '../components/GenericTable';
import GenericForm from '../components/GenericForm';
import styles from '../components/AdminPage.module.css';
import { Plus } from 'lucide-react';

const AdminResourcePage = () => {
    const { resourceName } = useParams();
    const config = resources[resourceName];
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(false);
    const [editingItem, setEditingItem] = useState(null);
    const [showForm, setShowForm] = useState(false);

    const loadData = useCallback(async () => {
        if (!config) return;
        setLoading(true);
        try {
            // 获取所有数据（通过设置较大的每页数量）
            const res = await api.getList(resourceName, { per_page: 10000 });
            setData(res.data || []);
        } catch (err) {
            console.error(err);
            alert('加载失败');
        } finally {
            setLoading(false);
        }
    }, [config, resourceName]);

    useEffect(() => {
        loadData();
    }, [loadData]);

    const handleCreate = () => {
        setEditingItem(null);
        setShowForm(true);
    };

    const handleEdit = (item) => {
        setEditingItem(item);
        setShowForm(true);
    };

    const handleDelete = async (id) => {
        try {
            await api.remove(resourceName, id);
            loadData();
        } catch (err) {
            console.error(err);
            alert('删除失败: ' + (err.response?.data?.error || err.message));
        }
    };

    const handleSubmit = async (formData) => {
        try {
            if (editingItem) {
                await api.update(resourceName, editingItem.id, formData);
            } else {
                await api.create(resourceName, formData);
            }
            setShowForm(false);
            loadData();
        } catch (err) {
            console.error(err);
            alert('保存失败: ' + (err.response?.data?.error || err.message));
        }
    };

    if (!config) return <div>Resource not found</div>;

    return (
        <div>
            <div className={styles.header}>
                <h2 className={styles.title}>{config.label}</h2>
                <button 
                    onClick={handleCreate}
                    className={styles.createBtn}
                    style={{ display: 'flex', alignItems: 'center', gap: 8 }}
                >
                    <Plus size={18} />
                    新建
                </button>
            </div>

            {loading ? (
                <div>Loading...</div>
            ) : (
                <GenericTable 
                    columns={config.columns} 
                    data={data} 
                    onEdit={handleEdit} 
                    onDelete={handleDelete} 
                />
            )}

            {showForm && (
                <GenericForm 
                    fields={config.fields} 
                    initialData={editingItem} 
                    key={editingItem?.id || 'new'}
                    onSubmit={handleSubmit} 
                    onCancel={() => setShowForm(false)} 
                />
            )}
        </div>
    );
};

export default AdminResourcePage;
