// // frontend/src/components/EventsPage.js
// import { useState, useEffect } from 'react';
// import axios from 'axios';
// import './EventsPage.css'; // We will create this file next

// function EventsPage() {
//   // 'useState' creates a state variable to store our list of events
//   const [events, setEvents] = useState([]);

//   useEffect(() => {
//     // Fetch events from the Django API
//     axios.get('http://127.0.0.1:8000/api/events/')
//       .then(response => {
//         // Update the state with the fetched events
//         setEvents(response.data);
//       })
//       .catch(error => {
//         console.error('There was an error fetching the events!', error);
//       });
//   }, []);

//   return (
//     <div className="events-container">
//       <h2>Events & Rules</h2>
//       {events.map(event => (
//         <div key={event.id} className="event-card">
//           <h3>{event.name}</h3>
//           <p className="event-category"><strong>Category:</strong> {event.category}</p>
//           <p className="event-rules"><strong>Rules:</strong> {event.rules || "No rules specified."}</p>
//         </div>
//       ))}
//     </div>
//   );
// }

// export default EventsPage;