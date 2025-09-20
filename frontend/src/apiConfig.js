// const API_BASE_URL = process.env.REACT_APP_API_BASE_URL;
// export default API_BASE_URL;

// In frontend/src/apiConfig.js

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://127.0.0.1:8000/api';

export default { API_BASE_URL };