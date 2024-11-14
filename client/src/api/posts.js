import axios from 'axios';

const API_URL = "http://localhost:5000/api";

// Fetch all posts with authentication
export const fetchPosts = async () => {
  try {
    // Retrieve the auth token from localStorage
    const authToken = localStorage.getItem("authToken");

    // If token is not found, return an empty array
    if (!authToken) {
      console.error("No token found. Please login.");
      return [];
    }

    // Make GET request with Authorization header
    const response = await axios.get(`${API_URL}/posts`, {
      headers: {
        Authorization: `Bearer ${authToken}`,  // Send token in the Authorization header
      },
    });

    return response.data; // Return the posts if the API call is successful
  } catch (error) {
    console.error("Error fetching posts:", error);
    // Return an empty array if there's an error
    return [];
  }
};

export const likePost = async (postId, username ) => {
  try {
    // Get token from localStorage
    const authToken = localStorage.getItem("authToken");

    // Make POST request with Authorization header
    const response = await axios.post(`${API_URL}/like`, 
      { post_id: postId, username },
      {
        headers: {
          Authorization: `Bearer ${authToken}` // Include the token in headers
        }
      }
    );
    
    return response.data; // Return the data from backend (success and message)
  } catch (error) {
    console.error("Error liking post:", error);
    throw new Error("Failed to like post");
  }
};