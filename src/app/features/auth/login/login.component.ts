import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router, ActivatedRoute } from '@angular/router';
import { AuthService } from '../../../core/services/auth.service';
import { ToastService } from 'src/app/shared/toast.service';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent implements OnInit {
  loginForm!: FormGroup;
  isSubmitting = false;
  errorMessage: string | null = null;
  showPassword = false;
  returnUrl = '/dashboard';

  constructor(
    private fb: FormBuilder,
    private router: Router,
    private route: ActivatedRoute,
    private authService: AuthService,
    private toast:ToastService
  ) {}

  ngOnInit(): void {

  const savedEmail = localStorage.getItem('pantrypulse_remember_email') || '';
this.toast.consumePendingToast();
  this.returnUrl =
      this.route.snapshot.queryParams['returnUrl'] || '/dashboard';

  this.loginForm = this.fb.group({
      email: [savedEmail,[Validators.required,Validators.email]],
      password:['',[Validators.required,Validators.minLength(6)]],
      rememberMe:[!!savedEmail]
  });

  // 👇 Add this
  const navigation = this.router.getCurrentNavigation();

  const signupSuccess =
      navigation?.extras.state?.['signupSuccess'];

  if (signupSuccess) {

      setTimeout(() => {

          this.toast.success(
              'Welcome to PantryPulse!',
              'Your account has been created successfully. Please sign in.'
          );

      },200);

  }

}

  toggleShowPassword(): void {
    this.showPassword = !this.showPassword;
  }

  get f() {
    return this.loginForm.controls;
  }

  onSubmit(): void {
    this.errorMessage = null;

    if (this.loginForm.invalid) {
      this.loginForm.markAllAsTouched();
      return;
    }

    const { email, password, rememberMe } = this.loginForm.value;

    if (rememberMe) {
      localStorage.setItem('pantrypulse_remember_email', email);
    } else {
      localStorage.removeItem('pantrypulse_remember_email');
    }

    this.isSubmitting = true;

    this.authService.login({ email, password }).subscribe({
     next: () => {

  this.isSubmitting = false;

  this.toast.success(
    'Welcome Back!',
    'You have successfully signed in to PantryPulse.'
  );

  setTimeout(() => {
    this.router.navigateByUrl(this.returnUrl);
  }, 800);

},
    error: (err) => {

  this.isSubmitting = false;

  if (err.status === 400 || err.status === 401 || err.status === 403) {

    this.errorMessage = 'Invalid email or password.';

  } else if (err.status === 0) {

    this.errorMessage = 'Unable to connect to the server. Please try again later.';

  } else if (err.status >= 500) {

    this.errorMessage = 'Server error. Please try again later.';

  } else {

    this.errorMessage = 'Something went wrong. Please try again.';

  }

  this.toast.error(
    'Login Failed',
    this.errorMessage
  );

}
    });
  }
}
