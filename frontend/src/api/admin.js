import client from './client';

export const getList = async (resource, params) => {
    const response = await client.get(`/admin/${resource}`, { params });
    return response.data; // { data: [...], meta: {...} }
};

export const getDetail = async (resource, id) => {
    const response = await client.get(`/admin/${resource}/${id}`);
    return response.data;
};

export const create = async (resource, data) => {
    const response = await client.post(`/admin/${resource}`, data);
    return response.data;
};

export const update = async (resource, id, data) => {
    const response = await client.put(`/admin/${resource}/${id}`, data);
    return response.data;
};

export const remove = async (resource, id) => {
    const response = await client.delete(`/admin/${resource}/${id}`);
    return response.data;
};
