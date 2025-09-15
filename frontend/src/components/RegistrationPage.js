// frontend/src/components/RegistrationPage.js
import { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  Paper, Box, Typography, TextField, Button, MenuItem, Stepper, Step, StepLabel,
  RadioGroup, FormControlLabel, Radio, FormControl, FormLabel, FormGroup, Checkbox, Link,
  InputLabel, Select, CircularProgress
} from '@mui/material';
import { API_BASE_URL } from '../apiConfig';
const steps = ['Personal Details', 'Select Category', 'Choose Competitions'];

function RegistrationPage() {
  const [activeStep, setActiveStep] = useState(0);
  const [isSuccess, setIsSuccess] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [hasTriedSubmit, setHasTriedSubmit] = useState(false);
  const [hasTriedNext, setHasTriedNext] = useState(false); // <-- new state

  const [formData, setFormData] = useState({
    fullName: '', email: '', state: '', gender: '', 
    groupId: '', categoryId: '', course: '', phoneNumber: '',
    events: {}
  });
  const [message, setMessage] = useState('');

  const [groups, setGroups] = useState([]);
  const [categories, setCategories] = useState([]);
  const [allEvents, setAllEvents] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [groupsRes, categoriesRes, eventsRes] = await Promise.all([
          axios.get(`${API_BASE_URL}/api/groups/`),
          axios.get(`${API_BASE_URL}/api/categories/`),
          axios.get(`${API_BASE_URL}/api/events/`)
        ]);
        setGroups(groupsRes.data);
        setCategories(categoriesRes.data);
        setAllEvents(eventsRes.data);
      } catch (error) { console.error("Error fetching form data!", error); }
    };
    fetchData();
  }, []);

  // Clear messages when switching steps
  useEffect(() => {
    setMessage('');
    setHasTriedSubmit(false);
    setHasTriedNext(false); // <-- also reset Next attempt
  }, [activeStep]);

  const validateStep = (step) => {
    if (step === 0) {
      const { fullName, email, state, gender, groupId, course, phoneNumber } = formData;
      if (!fullName || !email || !state || !gender || !groupId || !course || !phoneNumber) {
        setMessage("Please fill all required fields before proceeding.");
        return false;
      }
    }
    if (step === 1) {
      if (!formData.categoryId) {
        setMessage("Please select a category before proceeding.");
        return false;
      }
    }
    return true;
  };

  const handleNext = () => {
    setHasTriedNext(true); // <-- mark that user clicked Next
    setMessage('');
    setHasTriedSubmit(false);
    if (validateStep(activeStep)) {
      setActiveStep((prev) => prev + 1);
      setHasTriedNext(false); // <-- reset on successful step
    }
  };

  const handleBack = () => {
    setMessage('');
    setHasTriedSubmit(false);
    setActiveStep((prev) => prev - 1);
  };

  const handleReset = () => {
    setActiveStep(0);
    setIsSuccess(false);
    setFormData({
      fullName: '', email: '', state: '', gender: '', groupId: '',
      categoryId: '', course: '', phoneNumber: '', events: {}
    });
    setMessage('');
    setHasTriedSubmit(false);
    setHasTriedNext(false);
  };

  const handleChange = (e) => {
    setFormData(prev => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleCheckboxChange = (e) => {
    const name = e.target.name;
    const checked = e.target.checked;
    setFormData(prev => {
      const newEvents = { ...prev.events, [name]: checked };
      const anySelected = Object.values(newEvents).some(v => v);
      if (anySelected && message === "Please select at least one competition.") {
        setMessage('');
        setHasTriedSubmit(false);
      }
      return { ...prev, events: newEvents };
    });
  };
  
  const handleSubmit = async (e) => {
    if (e && e.preventDefault) e.preventDefault();

    setHasTriedSubmit(true);
    setMessage('');
    setIsSubmitting(true);

    const selectedEventIDs = Object.keys(formData.events).filter(id => formData.events[id]);
    if (selectedEventIDs.length === 0) {
      setMessage("Please select at least one competition.");
      setIsSubmitting(false);
      return;
    }
    
    const contestantPayload = {
      full_name: formData.fullName,
      email: formData.email,
      state: formData.state,
      gender: formData.gender,
      group: formData.groupId,
      category: formData.categoryId,
      course: formData.course,
      phone_number: formData.phoneNumber,
    };

    try {
      const contestantResponse = await axios.post(`${API_BASE_URL}/api/contestants/`, contestantPayload);
      const contestantId = contestantResponse.data.id;

      const registrationPromises = selectedEventIDs.map(eventId => {
        return axios.post(`${API_BASE_URL}/api/registrations/`, {
          contestant: contestantId,
          event: eventId
        });
      });
      await Promise.all(registrationPromises);
      setIsSuccess(true);
    } catch (error) {
      console.error('Submission error! Details:', error.response?.data);
      const details = error.response?.data;
      let userMessage = 'Registration failed. Please fill all required fields.';
      if (details?.email) { userMessage = `Email Error: ${details.email[0]}`; }
      setMessage(userMessage);
    } finally {
      setIsSubmitting(false);
    }
  };
  
  const getEligibleEvents = () => {
    if (!formData.categoryId) return [];
    const selectedCategory = categories.find(c => c.id === formData.categoryId);
    if (!selectedCategory) return [];
    return allEvents.filter(event => event.category === selectedCategory.name);
  };
  
  const getStepContent = (step) => {
    switch (step) {
      case 0:
        return (
          <>
            <TextField name="fullName" label="Full Name" value={formData.fullName} onChange={handleChange} fullWidth sx={{ mb: 2 }} />
            <TextField name="email" label="Email" type="email" value={formData.email} onChange={handleChange} fullWidth sx={{ mb: 2 }} />
            <TextField name="state" label="State" value={formData.state} onChange={handleChange} fullWidth sx={{ mb: 2 }} />
            <FormControl sx={{ mb: 2 }}>
              <FormLabel>Gender</FormLabel>
              <RadioGroup row name="gender" value={formData.gender} onChange={handleChange}>
                <FormControlLabel value="Male" control={<Radio />} label="Male" />
                <FormControlLabel value="Female" control={<Radio />} label="Female" />
              </RadioGroup>
            </FormControl>
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>School of Studies</InputLabel>
              <Select name="groupId" value={formData.groupId} label="School of Studies" onChange={handleChange}>
                {groups.map(group => <MenuItem key={group.id} value={group.id}>{group.name}</MenuItem>)}
              </Select>
            </FormControl>
            <TextField name="course" label="Course" value={formData.course} onChange={handleChange} fullWidth sx={{ mb: 2 }} />
            <TextField name="phoneNumber" label="Phone Number" value={formData.phoneNumber} onChange={handleChange} fullWidth sx={{ mb: 2 }} />
          </>
        );
      case 1:
        return (
           <>
           {/* <Paper elevation={0} sx={{ mt: 2, borderRadius: 2, overflow: 'hidden', border: '1px solid #ddd' }}>
              <Box sx={{ backgroundColor: '#fefefeff', color: 'white', px: 2, py: 1.5 }}>
                <Typography variant="h6">Note</Typography>
              </Box>
              <Box sx={{ p: 2, backgroundColor: '#f5f5f5' }}>
                <Typography>
                  Boys Category A - UG <br />
                  Boys Category B - PG & PhD 
                </Typography>
              </Box>
            </Paper> */}
            
            <FormControl fullWidth required sx={{ mt: 2 }}>
              <InputLabel>Your Category</InputLabel>
              <Select name="categoryId" value={formData.categoryId} label="Your Category" onChange={handleChange}>
                {categories.map(cat => <MenuItem key={cat.id} value={cat.id}>{cat.name}</MenuItem>)}
              </Select>
            </FormControl>
            
            
          </> 
        );
      case 2:
        const eligibleEvents = getEligibleEvents();
        return (
          <FormGroup>
            {eligibleEvents.length > 0 ? eligibleEvents.map(event => (
              <FormControlLabel 
                key={event.id} 
                control={<Checkbox checked={!!formData.events[event.id]} onChange={handleCheckboxChange} name={String(event.id)} />} 
                label={event.name}
              />
            )) : <Typography>Please select your category to see eligible events.</Typography>}
          </FormGroup>
        );
      default: return 'Unknown step';
    }
  };

  return (
    <Box sx={{ display: 'flex', justifyContent: 'center', py: 5 }}>
      <Paper elevation={6} sx={{ p: { xs: 3, md: 5 }, borderRadius: 4, maxWidth: '600px', width: '100%' }}>
        {isSuccess ? (
          <Box sx={{ textAlign: 'center' }}>
            <Typography variant="h5" sx={{ fontWeight: 'bold', color: 'green', mb: 2 }}>
              Congratulations!
            </Typography>
            <Typography>
              You are successfully registered for PU Sahithyolsav.
            </Typography>
            <Typography sx={{ my: 2 }}>
              Please join this WhatsApp group for program updates: 
              <Link href="https://chat.whatsapp.com/JX3jdMNIOJaLUnwVSAXvH8?mode=ems_copy_t" target="_blank"> Join Group</Link>
            </Typography>
            <Typography>
              Thank you for participating, wishing you all the best.
            </Typography>
            <Button variant="contained" onClick={handleReset} sx={{ mt: 4 }}>
              Register Another Participant
            </Button>
          </Box>
        ) : (
          <>
            <Stepper activeStep={activeStep} alternativeLabel sx={{ mb: 4 }}>
              {steps.map((label) => <Step key={label}><StepLabel>{label}</StepLabel></Step>)}
            </Stepper>

            <form noValidate>
              {getStepContent(activeStep)}
              <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 4 }}>
                {activeStep !== 0 && (
                  <Button type="button" onClick={handleBack} sx={{ mr: 1 }}>
                    Back
                  </Button>
                )}
                
                {activeStep === steps.length - 1 ? (
                  <Button 
                    variant="contained" 
                    type="button" 
                    onClick={handleSubmit}
                    disabled={isSubmitting}
                  >
                    {isSubmitting ? <CircularProgress size={24} color="inherit" /> : 'Register'}
                  </Button>
                ) : (
                  <Button 
                    variant="contained" 
                    type="button" 
                    onClick={handleNext}
                  >
                    Next
                  </Button>
                )}
              </Box>
            </form>

            {/* show error message for current step */}
            {(hasTriedNext || hasTriedSubmit) && message && (
              <Typography sx={{ mt: 2, fontWeight: 'bold', color: 'red', textAlign: 'center' }}>
                {message}
              </Typography>
            )}
          </>
        )}
      </Paper>
    </Box>
  );
}

export default RegistrationPage;
