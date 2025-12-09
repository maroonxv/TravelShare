import axios from 'axios';

const client = axios.create({
    baseURL: '/api',
    withCredentials: true, // Important for session cookies
    headers: {
        'Content-Type': 'application/json',
    },
});

// Response interceptor to handle 401 (Unauthorized)
client.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response && error.response.status === 401) {
            // If we are not already on login/register pages, redirect?
            // For now, just pass the error, let AuthContext handle it.
            // But maybe we emit an event or clear local state.
        }
        return Promise.reject(error);
    }
);

export default client;
