import axios from 'axios';

// API URL for the backend
const API_URL = "http://localhost:5000/api";

// Function to post news to the backend
export const postNews = async (newsText, authToken) => {
  try {
    const response = await axios.post(
      `${API_URL}/post`, 
      { newsText }, 
      { headers: { Authorization: `Bearer ${authToken}` } }
    );
    return response.data;  // Return the success message from the API
  } catch (error) {
    console.error("Error posting news:", error);
    return error.response ? error.response.data : { error: "Network error" };
  }
};
