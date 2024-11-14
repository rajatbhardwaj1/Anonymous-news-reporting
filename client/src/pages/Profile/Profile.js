import React, { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../../context/AuthContext';
import axios from 'axios';
import './Profile.css';
import { resolvePath } from 'react-router-dom';
import { getTimeSlot } from '../../api/time_slot';  // Import the function from timeslot.js


const ReputationDeclarations = ({ username, authToken, currentPseudonym }) => {
  const [repDeclarations, setRepDeclarations] = useState([]);
  const [TRV, setTRV] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentStep, setCurrentStep] = useState(null);

  useEffect(() => {
    const fetchRepDeclarations = async () => {
      try {
        const response = await axios.get('http://localhost:5000/api/get_rep_dec', {
          headers: { Authorization: `Bearer ${authToken}` },
          params: { username }
        });

        if (response.data.success) {
          setRepDeclarations(response.data.rep_dec || []);
          setError(null);
        } else {
          setError("Failed to fetch reputation declarations.");
        }
      } catch (error) {
        console.error("Error fetching reputation declarations:", error);
        setError("Error fetching reputation declarations. Please try again.");
      } finally {
        setLoading(false);
      }
    };

    const fetchTRV = async () => {
      try {
        const response = await axios.get('http://localhost:5000/api/get_trv', {
          headers: { Authorization: `Bearer ${authToken}` },
          params: { username }
        });

        if (response.data.success) {
          setTRV(response.data.trv || []);
          setError(null);
        } else {
          setError("Failed to fetch TRV.");
        }
      } catch (error) {
        console.error("Error fetching TRV:", error);
        setError("Error fetching TRV. Please try again.");
      } finally {
        setLoading(false);
      }
    };

    fetchRepDeclarations();
    fetchTRV();
  }, [authToken, username]);

  const handleAnonymityStep = async (serialNo) => {
    setCurrentStep('Anonymity');
    try {
      const response = await axios.post('http://localhost:5000/api/anonymity_step', 
      { username, serial_no: serialNo }, 
      { headers: { Authorization: `Bearer ${authToken}` } });

      if (response.data.success) {
        alert('Anonymity Step Completed: TRV Created');
        window.location.reload();

      } else {
        alert('Error in Anonymity Step');
      }
    } catch (error) {
      console.error("Error in anonymity step:", error);
      alert('Error completing anonymity step');
    }
  };

  const handleEndorsementStep = async (trvSerialNo) => {
    setCurrentStep('Endorsement');
    try {
      const response = await axios.post('http://localhost:5000/api/endorsement_step', 
      { username, trv_serial_no: trvSerialNo }, 
      { headers: { Authorization: `Bearer ${authToken}` } });

      if (response.data.success) {
        alert('Endorsement Step Completed: Reputation Endorsed');
        window.location.reload();
      } else {
        alert('Error in Endorsement Step');
      }
    } catch (error) {
      console.error("Error in endorsement step:", error);
      alert('Error completing endorsement step');
    }
  };

  if (loading) return <p>Loading reputation declarations...</p>;
  if (error) return <p>{error}</p>;

  return (
    <div className="reputation-declarations">
      <h3>Reputation Declarations</h3>
      <ul>
        {repDeclarations.map((declaration, index) => {
          const cipibPseudonym = declaration.Cipib?.pseudonym;
          const isOutdated = cipibPseudonym !== currentPseudonym;

          return (
            <li key={index}>
              <strong>Serial No:</strong> {declaration.serial_no}
              <p>Status: {isOutdated ? 'Outdated' : 'Not Outdated'}</p>
              {isOutdated && (
                <div>
                  <button onClick={() => handleAnonymityStep(declaration.serial_no)}>Anonymity</button>
                 
                </div>
              )}
            </li>
          );
        })}
      </ul>
      <h3>TRV</h3>
      <ul>
        {TRV.map((trvItem, index) => (
          <li key={index}>
            <p><strong>TRV Serial No:</strong> {trvItem.trv_serial_no}</p>
            <button onClick={() => handleEndorsementStep(trvItem.trv_serial_no)}>Endorsement</button>
          </li>
        ))}
      </ul>
    </div>
  );
};



const Profile = () => {
  const { user, authToken } = useContext(AuthContext);
  const [newsText, setNewsText] = useState('');
  const [message, setMessage] = useState('');
  const [pseudonym, setPseudonym] = useState(null);
  const [pseudonymStatus, setPseudonymStatus] = useState('');

  // Fetch pseudonym and verify it
  useEffect(() => {
    if (authToken && user?.username) {
      fetchAndVerifyPseudonym();
    }
  }, [authToken, user?.username]);

  const fetchAndVerifyPseudonym = async () => {
    try {

      const current_timeSlot = await getTimeSlot();
      if (current_timeSlot === null) {
        setPseudonymStatus("Failed to fetch current time slot. Please try again.");
        return;
      }

      // Fetch the user's time_slot from the backend
      const userTimeSlotResponse = await axios.get('http://localhost:5000/api/user_time_slot', {
        params: { username: user.username },
        headers: { Authorization: `Bearer ${authToken}` }
      });

      if (!userTimeSlotResponse.data.success) {
        setPseudonymStatus(userTimeSlotResponse.data.message);
        return;
      }

      const userTimeSlot = userTimeSlotResponse.data.time_slot;
      console.log("current timeslot ")
      console.log(current_timeSlot)
      console.log("user timeslot ")
      console.log(userTimeSlot)

      if (current_timeSlot === userTimeSlot) {
        setPseudonymStatus("Pseudonym is valid.");
      } else {
        setPseudonymStatus("Pseudonym is invalid. Generate a new one...");
        // await assignPseudonym(); // Generate a new pseudonym if invalid
        return;
      }


      const response = await axios.get('http://localhost:5000/api/user_info', {
        headers: { Authorization: `Bearer ${authToken}` },
        params: { username: user.username }
      });
      const fetchedPseudonym = response.data.pseudonym || 'Not Assigned';
      setPseudonym(fetchedPseudonym);

      if (fetchedPseudonym !== 'Not Assigned') {

        await verifyPseudonym();
      }
    } catch (error) {
      console.error("Error fetching pseudonym:", error);
    }
  };

  const assignPseudonym = async () => {
    try {
      const timeSlot = await getTimeSlot();

      if (timeSlot === null) {
        setPseudonymStatus("Failed to fetch time slot. Please try again.");
        return;
      }

      const response = await axios.post('http://localhost:5000/api/issue_pseudonym',
        { username: user.username },
        { headers: { Authorization: `Bearer ${authToken}` } }
      );
      if (response.data.success) {
        setPseudonym(response.data.pseudonym);
        setPseudonymStatus('Pseudonym issued successfully');
      } else {
        setPseudonymStatus(response.data.error || 'Failed to assign pseudonym');
      }
    } catch (error) {
      console.error("Error assigning pseudonym:", error);
      setPseudonymStatus("Failed to assign pseudonym. Please try again.");
    }
  };

  const verifyPseudonym = async () => {
    try {

      const timeSlot = await getTimeSlot();

      if (timeSlot === null) {
        setPseudonymStatus("Failed to fetch time slot. Please try again.");
        return;
      }
      const response = await axios.post('http://localhost:5000/api/verify_pseudonym',
        { time_slot: timeSlot, username: user.username },
        { headers: { Authorization: `Bearer ${authToken}` } }
      );
      setPseudonymStatus(response.data.success ? response.data.message : response.data.error || 'Pseudonym verification failed');
    } catch (error) {
      console.error("Error verifying pseudonym:", error);
      setPseudonymStatus('Failed to verify pseudonym');
    }
  };

  const postNews = async (e) => {
    e.preventDefault();

    if (!newsText.trim()) {
      setMessage('Please enter some text to post.');
      return;
    }

    try {
      const response = await axios.post('http://localhost:5000/api/post',
        { newsText, username: user.username },
        { headers: { Authorization: `Bearer ${authToken}` } }
      );
      setMessage(response.data.message || 'News posted successfully!');
      setNewsText('');
    } catch (error) {
      console.error('Error posting news:', error);
      setMessage('Failed to post news. Please try again.');
    }
  };

  return (
    <div className="profile-container">
      <h2>Welcome, {user?.username}!</h2>

      <div className="pseudonym-section">
        <p>Pseudonym: {pseudonym || 'Not Assigned'}</p>
        <p>Status: {pseudonymStatus}</p>
        <button onClick={assignPseudonym}>Assign Pseudonym</button>
      </div>

      <ReputationDeclarations
        username={user?.username}
        authToken={authToken}
        currentPseudonym={pseudonym}
      />
      <div className="post-news">
        <h3>Post News</h3>
        <form onSubmit={postNews}>
          <textarea
            value={newsText}
            onChange={(e) => setNewsText(e.target.value)}
            placeholder="Write something..."
            rows="4"
            cols="90"
            required
          />
          <button className="submit-news" type="submit">Post News</button>
        </form>
      </div>

      {message && <p className="message">{message}</p>}
    </div>
  );
};

export default Profile;
