// src/pages/Login/Login.js
import React, { useState, useContext } from 'react';
import { AuthContext } from '../../context/AuthContext';
import { useNavigate } from 'react-router-dom'; // Import useNavigate
import './Login.css';

function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const { handleLogin } = useContext(AuthContext);
  const navigate = useNavigate(); // Initialize navigate function

  const onSubmit = async () => {
  const error = await handleLogin(username, password);
  if (error) {
    setMessage(error);  // Set error message if any
  } else {
    setMessage("Login successful! Redirecting to home...");
    navigate("/home");  // Proceed to home page
  }
};

  return (
    <div className="login-container">
      <h2>Login</h2>
      <input
        type="text"
        placeholder="Username"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
      />
      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      <button onClick={onSubmit}>Login</button>
      <p>{message}</p>
    </div>
  );
}

export default Login;
