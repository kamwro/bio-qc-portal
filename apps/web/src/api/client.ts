import axios from 'axios';

const BASE = import.meta.env.VITE_API_URL ? `${import.meta.env.VITE_API_URL}/api` : '/api';

export const apiClient = axios.create({ baseURL: BASE });
