import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL;

// Add an Authorization header for the token
const setAuthToken = (token) => {
  if (token) {
    axios.defaults.headers.common["Authorization"] = `Bearer ${token}`;
  } else {
    delete axios.defaults.headers.common["Authorization"];
  }
};

export const loginUser = async (username, password) => {
  try {
    const response = await axios.post(`${API_URL}/login`, { username, password });
    return response.data;
  } catch (error) {
    console.error("Error during login:", error);
    return { error: "Invalid login credentials" };
  }
};

export const registerUser = async (username, password) => {
  try {
    const response = await axios.post(`${API_URL}/register`, { username, password });
    return response.data;
  } catch (error) {
    console.error("Error registering user:", error);
    return error.response ? error.response.data : { error: "Network error" };
  }
};
