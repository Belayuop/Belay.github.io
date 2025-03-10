const express = require('express');
const bodyParser = require('body-parser');
const nodemailer = require('nodemailer');

const app = express();
const PORT = process.env.PORT || 5000;

// Middleware to parse JSON request body
app.use(bodyParser.json());

// Serve static files (your frontend)
app.use(express.static('public'));

// Route for contact form submission
app.post('/contact', (req, res) => {
    const { name, email, message } = req.body;

    // Create a transporter for sending emails (using Gmail SMTP)
    const transporter = nodemailer.createTransport({
        service: 'gmail',
        auth: {
            user: 'your-email@gmail.com', // Replace with your email
            pass: 'your-email-password',  // Replace with your email password
        },
    });

    // Email options
    const mailOptions = {
        from: email,
        to: 'your-email@gmail.com',  // Replace with your email
        subject: `New message from ${name}`,
        text: `Message: ${message}\nFrom: ${name} (${email})`,
    };

    // Send the email
    transporter.sendMail(mailOptions, (error, info) => {
        if (error) {
            console.log(error);
            return res.json({ status: 'error', message: error });
        } else {
            console.log('Email sent: ' + info.response);
            return res.json({ status: 'success', message: 'Message sent successfully' });
        }
    });
});

// Start the server
app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});
