import React, { useState, useContext } from 'react';
import { AuthContext } from '../../context/AuthContext';
import './Register.css';

function Register() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const { handleRegister } = useContext(AuthContext);

  const onSubmit = async () => {
    const feedback = await handleRegister(username, password);
    setMessage(feedback);
  };

  return (
    <div className="register-container">
      <h2>Register</h2>
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
      <button onClick={onSubmit}>Register</button>
      <p>{message}</p>
    </div>
  );
}

export default Register;
