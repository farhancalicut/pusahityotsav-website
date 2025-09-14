// frontend/src/components/PointsTable.js
import { useState, useEffect } from 'react';
import axios from 'axios';
import './PointsTable.css'; // We'll create this file next

function PointsTable() {
  const [points, setPoints] = useState([]);

  const fetchPoints = async () => {
    try {
      const response = await axios.get('http://127.0.0.1:8000/api/sahityotsav/points/');
      setPoints(response.data);
    } catch (error) {
      console.error('Error fetching points!', error);
    }
  };

  useEffect(() => {
    fetchPoints(); // Fetch points initially
    const interval = setInterval(fetchPoints, 10000); // Refresh every 10 seconds
    return () => clearInterval(interval); // Cleanup on unmount
  }, []);

  return (
    <div className="points-table-container">
      <h2>Group Points</h2>
      <table className="points-table">
        <thead>
          <tr>
            <th>Rank</th>
            <th>Group Name</th>
            <th>Total Points</th>
          </tr>
        </thead>
        <tbody>
          {points.map((group, index) => (
            <tr key={group.group_name}>
              <td data-label="Rank">{index + 1}</td>
              <td data-label="Group Name">{group.group_name}</td>
              <td data-label="Total Points">{group.total_points}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default PointsTable;