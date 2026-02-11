import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css'],
  imports: [FormsModule, CommonModule, RouterLink]
})
export class LoginComponent {
  // Fields for email, password, and error/status messages
  email: string = '';
  password: string = '';
  errorMessage: string = '';
  statusMessage: string = '';
  messageType: string = '';

  // Object to hold validation error messages
  errors: any = {
    email: '',
    password: '',
  };

  // Field for password visibility toggle
  passwordFieldType: string = 'password';

  constructor(private router: Router) {}

  // Toggle password visibility
  togglePasswordVisibility() {
    this.passwordFieldType = this.passwordFieldType === 'password' ? 'text' : 'password';
  }

  // Validate email format
  validateEmail() {
    if (!this.email) {
      this.errors.email = 'Email is required';
      return;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    this.errors.email = emailRegex.test(this.email)
      ? ''
      : 'Please enter a valid email address';
  }

  // Validate password strength
  validatePassword() {
    if (!this.password) {
      this.errors.password = 'Password is required';
      return;
    }

    const passwordRegex = /^(?=.*[A-Za-z])(?=.*\d).{8,}$/;
    this.errors.password = passwordRegex.test(this.password)
      ? ''
      : 'Password must be at least 8 characters with at least one letter and one number';
  }

  // Check if any validation errors exist
  hasErrors(): boolean {
    return Object.values(this.errors).some(error => error !== '');
  }

  // Handle the login process
  login() {
    // Validate all fields on submit
    this.validateEmail();
    this.validatePassword();

    // Check if there are any validation errors
    if (this.hasErrors()) {
      this.errorMessage = 'Please correct the errors before continuing';
      return;
    }

    // Prepare the user credentials to send in the request
    const userCredentials = {
      email: this.email,
      password: this.password,
    };

    // Make the login request to the server
    fetch('http://127.0.0.1:5000/api/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(userCredentials),
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error(`HTTP Error: ${response.status}`);
        }
        return response.json();
      })
      .then((data) => {
        // Handle success or failure based on response data
        if (data.status === 'success' && data.accountActivated) {
          this.statusMessage = 'Login successful. Welcome!';
          this.messageType = 'success';
          this.router.navigate(['/home']);
        } else if (data.status === 'success' && !data.accountActivated) {
          this.statusMessage = 'Your account is not activated yet. Please check your email.';
          this.messageType = 'error';
        } else {
          this.statusMessage = 'Incorrect username or password.';
          this.messageType = 'error';
        }
      })
      .catch((error) => {
        // Handle errors during the login process
        console.error('Error during login:', error);
        this.statusMessage = 'An error occurred. Please try again.';
        this.messageType = 'error';
      });
  }
}
