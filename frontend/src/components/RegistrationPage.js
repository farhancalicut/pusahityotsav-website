// frontend/src/components/RegistrationPage.js
import { useState, useEffect } from "react";
import axios from "axios";
import {
  Paper, Box, Typography, TextField, Button, MenuItem, Stepper, Step, StepLabel,
  RadioGroup, FormControlLabel, Radio, FormControl, FormLabel, FormGroup,
  Checkbox, Link, InputLabel, Select, CircularProgress,
} from "@mui/material";
import WhatsAppIcon from '@mui/icons-material/WhatsApp';
import API_BASE_URL from '../apiConfig';

const steps = ["Personal Details", "Select Category", "Choose Competitions"];

function RegistrationPage() {
  const [activeStep, setActiveStep] = useState(0);
  const [isSuccess, setIsSuccess] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [hasTriedNext, setHasTriedNext] = useState(false);
  const [hasTriedSubmit, setHasTriedSubmit] = useState(false);
  const [message, setMessage] = useState("");

  const [formData, setFormData] = useState({
    fullName: "",
    email: "",
    state: "",
    gender: "",
    groupId: "",
    categoryId: "",
    course: "",
    phoneNumber: "",
    events: {},
  });

  const [groups, setGroups] = useState([]);
  const [categories, setCategories] = useState([]);
  const [events, setEvents] = useState([]); // This will hold the dynamically loaded, eligible events

  // This useEffect runs once to get the initial dropdown data for groups and categories
  useEffect(() => {
    const fetchInitialData = async () => {
      try {
        const [groupsRes, categoriesRes] = await Promise.all([
          axios.get(`${API_BASE_URL}/api/groups/`),
          axios.get(`${API_BASE_URL}/api/categories/`),
        ]);
        setGroups(groupsRes.data);
        setCategories(categoriesRes.data);
      } catch (error) {
        console.error("Error fetching initial data!", error);
      }
    };
    fetchInitialData();
  }, []);

  // This useEffect runs ONLY when the user selects a category
  useEffect(() => {
    if (formData.categoryId) { // Check if a category has been selected
      const fetchEvents = async () => {
        try {
          // Call the new, smarter API endpoint with the category ID
          const response = await axios.get(`${API_BASE_URL}/api/events-for-registration/${formData.categoryId}/`);
          setEvents(response.data);
        } catch (error) {
          console.error("Error fetching events for category!", error);
        }
      };
      fetchEvents();
    } else {
      // If no category is selected, the events list should be empty
      setEvents([]);
    }
  }, [formData.categoryId]); // The dependency array ensures this runs only when the category ID changes

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
    setHasTriedNext(true);
    setMessage("");
    if (validateStep(activeStep)) {
      setActiveStep((prev) => prev + 1);
      setHasTriedNext(false);
    }
  };

  const handleBack = () => {
    setMessage("");
    setActiveStep((prev) => prev - 1);
  };

  const handleReset = () => {
    setActiveStep(0);
    setIsSuccess(false);
    setFormData({
      fullName: "", email: "", state: "", gender: "", groupId: "",
      categoryId: "", course: "", phoneNumber: "", events: {},
    });
    setMessage("");
    setHasTriedNext(false);
    setHasTriedSubmit(false);
  };

  const handleChange = (e) => {
    setFormData((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleCheckboxChange = (e) => {
    const name = e.target.name;
    const checked = e.target.checked;
    setFormData((prev) => ({
      ...prev,
      events: { ...prev.events, [name]: checked },
    }));
  };

  const handleSubmit = async (e) => {
    if (e && e.preventDefault) e.preventDefault();
    setHasTriedSubmit(true);
    setMessage("");
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
      const registrationPromises = selectedEventIDs.map((eventId) => {
        return axios.post(`${API_BASE_URL}/api/registrations/`, {
          contestant: contestantId,
          event: eventId,
        });
      });
      await Promise.all(registrationPromises);
      setIsSuccess(true);
    } catch (error) {
      console.error("Submission error! Details:", error.response?.data);
      setMessage("Registration failed. Please check your details and try again.");
    } finally {
      setIsSubmitting(false);
    }
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
                {groups.map((group) => (
                  <MenuItem key={group.id} value={group.id}>{group.name}</MenuItem>
                ))}
              </Select>
            </FormControl>
            <TextField name="course" label="Course" value={formData.course} onChange={handleChange} fullWidth sx={{ mb: 2 }} />
            <TextField name="phoneNumber" label="Phone Number" value={formData.phoneNumber} onChange={handleChange} fullWidth sx={{ mb: 2 }} />
          </>
        );
      case 1:
        return (
          <>
          <Paper elevation={0} sx={{ mt: 2, borderRadius: 2, overflow: "hidden", border: "1px solid #ddd" }}>
              <Box sx={{ backgroundColor: "#1a5b00ff", color: "white", px: 2, py: 1.5 }}>
                <Typography variant="h6">Note</Typography>
              </Box>
              <Box sx={{ p: 2, backgroundColor: "#f5f5f5" }}>
                <Typography>
                  Category A - UG<br />
                  Category B - PG & PhD<br />
                </Typography>
              </Box>
            </Paper>

          <FormControl fullWidth required sx={{ mt: 2 }}>
            <InputLabel>Your Category</InputLabel>
            <Select name="categoryId" value={formData.categoryId} label="Your Category" onChange={handleChange}>
              {categories.map((cat) => (
                <MenuItem key={cat.id} value={cat.id}>{cat.name}</MenuItem>
              ))}
            </Select>
          </FormControl>
          </>
        );
      case 2:
        return (
          <>
            <Paper elevation={0} sx={{ mt: 2, borderRadius: 2, overflow: "hidden", border: "1px solid #ddd" }}>
              <Box sx={{ backgroundColor: "#1a5b00ff", color: "white", px: 2, py: 1.5 }}>
                <Typography variant="h6">Note</Typography>
              </Box>
              <Box sx={{ p: 2, backgroundColor: "#f5f5f5" }}>
                <Typography>
                  A person can participate upto four individual Programmes. Additionally there is no limits for participating in general items.
                </Typography>
              </Box>
            </Paper>
            <br />
            <FormGroup>
              {events.length > 0 ? (
                events.map((event) => (
                  <FormControlLabel
                    key={event.id}
                    control={
                      <Checkbox
                        checked={!!formData.events[event.id]}
                        onChange={handleCheckboxChange}
                        name={String(event.id)}
                      />
                    }
                    label={event.name}
                  />
                ))
              ) : (
                <Typography>Please select your category to see eligible events.</Typography>
              )}
            </FormGroup>
          </>
        );
      default:
        return "Unknown step";
    }
  };

  return (
    <Box sx={{ display: "flex", justifyContent: "center", py: 3 }}>
      <Paper
        // elevation={1}
        sx={{
          p: { xs: 6, md: 5 }, // smaller padding on mobile
          borderRadius: 2,
          maxWidth: { xs: '90%', sm: '80%', md: '600px' }, // responsive width
          width: '100%',
        }}
      >
        {isSuccess ? (
          <Box sx={{ textAlign: "center" }}>
            <Typography variant="h5" sx={{ fontWeight: "bold", color: "green", mb: 2 }}>Congratulations!</Typography>
            <Typography>You are successfully registered for PU Sahithyolsav.</Typography>
            <Typography sx={{ my: 2 }}>
                Please join this WhatsApp group for program updates:<br /><br />
                <Button
                  variant="contained"
                  color="success"
                  startIcon={<WhatsAppIcon />}
                  href="https://chat.whatsapp.com/CLtEVLigf2fJwZJM0Z5B9v?mode=ems_copy_c"
                  target="_blank"
                  sx={{ ml: 2 }}
                >
                  Join Group
                </Button>
              </Typography>
            <Typography>Thank you for participating, wishing you all the best.</Typography>
            <Button variant="contained" onClick={handleReset} sx={{ mt: 4 }}>Register Another Participant</Button>
          </Box>
        ) : (
          <>
            <Stepper activeStep={activeStep} alternativeLabel sx={{ mb: 4 }}>
              {steps.map((label) => (
                <Step key={label}><StepLabel>{label}</StepLabel></Step>
              ))}
            </Stepper>
            <form noValidate>
              {getStepContent(activeStep)}
              <Box sx={{ display: "flex", justifyContent: "flex-end", mt: 4 }}>
                {activeStep !== 0 && (<Button type="button" onClick={handleBack} sx={{ mr: 1 }}>Back</Button>)}
                {activeStep === steps.length - 1 ? (
                  <Button variant="contained" type="button" onClick={handleSubmit} disabled={isSubmitting}>
                    {isSubmitting ? <CircularProgress size={24} color="inherit" /> : "Register"}
                  </Button>
                ) : (
                  <Button variant="contained" type="button" onClick={handleNext}>Next</Button>
                )}
              </Box>
            </form>
            {(hasTriedNext || hasTriedSubmit) && message && (
              <Typography sx={{ mt: 2, fontWeight: "bold", color: "red", textAlign: "center" }}>
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