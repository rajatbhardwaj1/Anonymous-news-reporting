// timeslot.js
export const getTimeSlot = async () => {
    try {
      // Call the API endpoint to get the time slot
      const response = await fetch('http://localhost:5000/api/get_time_slot'); // Update with your actual backend URL
      
      // Check if the response is successful
      if (!response.ok) {
        throw new Error('Failed to fetch time slot: ' + response.statusText);
      }
  
      // Parse the JSON response
      const data = await response.json();
  
      if (data.success) {
        // Return the time slot from the response
        return data.timeSlot;
      } else {
        console.error(data.message || 'Failed to fetch time slot.');
        return null;  // Return null if the API call was not successful
      }
    } catch (error) {
      console.error('Error fetching time slot:', error);
      return null;  // Return null if there is an error
    }
  };
  