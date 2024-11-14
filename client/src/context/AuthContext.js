import React, { createContext, useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { loginUser, registerUser } from '../api/auth';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [authToken, setAuthToken] = useState(localStorage.getItem("authToken"));
  const [user, setUser] = useState(null);
  const navigate = useNavigate();

  // Initialize user state if authToken exists
  useEffect(() => {
    if (authToken) {
      // Decode token to get the username (if the token has 'username' embedded)
      const decodedToken = JSON.parse(atob(authToken.split('.')[1]));  // Decoding JWT
      setUser({ username: decodedToken.username });
    }
  }, [authToken]);

  // Login handler
  const handleLogin = async (username, password) => {
    try {
      const response = await loginUser(username, password);
      console.log("Login response:", response);

      // Check if response has the token
      if (response && response.token) {
        setAuthToken(response.token);
        setUser({ username });
        localStorage.setItem("authToken", response.token);
        localStorage.setItem("username", username);
        navigate("/home");
        return null;
      } else {
        // Return any error from the response
        return response?.error || "An error occurred during login.";
      }
    } catch (error) {
      console.error("Login error:", error);
      return "An error occurred during login.";
    }
  };

  // Register handler
  const handleRegister = async (username, password) => {
    try {
      const response = await registerUser(username, password);
      if (response.message) {
        navigate("/login");
        return response.message;
      } else {
        return response.error;
      }
    } catch (error) {
      console.error("Registration error:", error);
      return "An error occurred during registration.";
    }
  };

  // Logout handler
  const handleLogout = () => {
    setAuthToken(null);
    setUser(null);
    localStorage.removeItem("authToken");
    localStorage.removeItem("username");
    navigate("/login");
  };

  return (
    <AuthContext.Provider value={{ authToken, user, handleLogin, handleRegister, handleLogout }}>
      {children}
    </AuthContext.Provider>
  );
};
