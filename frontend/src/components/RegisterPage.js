import React, { useState } from 'react';
import { Eye, EyeOff, Mail, Lock, User, UserPlus, ArrowLeft } from 'lucide-react';
import { validateRegisterForm } from '../utils/validation';

export default function RegisterPage({ setCurrentPage }) {
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async () => {
    const newErrors = validateRegisterForm(formData);

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    setErrors({});
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: formData.email,
          password: formData.password,
          first_name: formData.firstName,
          last_name: formData.lastName
        })
      });

      const data = await response.json();

      if (response.ok) {
        alert('Registration successful! You can now login with your credentials.');
        setCurrentPage('login');
      } else {
        alert(data.detail || 'Registration failed. Please try again.');
      }
    } catch (error) {
      console.error('Registration error:', error);
      alert('Network error. Please check if the server is running.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));

    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  return (
    <div className="card-glass w-full max-w-md overflow-hidden animate-bounce-in">
      <div className="bg-gradient-to-r from-green-500/20 to-blue-600/20 backdrop-blur-sm p-8 text-center relative border-b border-white/10">
        <button
          onClick={() => setCurrentPage('login')}
          className="absolute left-4 top-4 text-white/80 hover:text-white transition-colors p-2 rounded-full hover:bg-white/10"
        >
          <ArrowLeft className="w-6 h-6" />
        </button>
        <div className="w-20 h-20 bg-gradient-to-r from-green-400 to-blue-500 rounded-full flex items-center justify-center mx-auto mb-4 shadow-2xl animate-pulse">
          <UserPlus className="w-10 h-10 text-white" />
        </div>
        <h1 className="text-3xl font-bold text-white mb-2 text-glow">Create Account</h1>
        <p className="text-green-100/80">Join us today</p>
      </div>

      <div className="p-8">
        <div className="space-y-5">
          <div className="grid grid-cols-2 gap-4">
            <div className="animate-slide-up">
              <label htmlFor="firstName" className="block text-sm font-medium text-white/90 mb-2">
                First Name
              </label>
              <input
                type="text"
                id="firstName"
                name="firstName"
                value={formData.firstName}
                onChange={handleInputChange}
                className={`input-glass w-full px-4 py-3 ${
                  errors.firstName ? 'border-red-400 focus:ring-red-400' : ''
                }`}
                placeholder="John"
              />
              {errors.firstName && (
                <p className="text-red-400 text-xs mt-1 animate-pulse">{errors.firstName}</p>
              )}
            </div>
            <div className="animate-slide-up">
              <label htmlFor="lastName" className="block text-sm font-medium text-white/90 mb-2">
                Last Name
              </label>
              <input
                type="text"
                id="lastName"
                name="lastName"
                value={formData.lastName}
                onChange={handleInputChange}
                className={`input-glass w-full px-4 py-3 ${
                  errors.lastName ? 'border-red-400 focus:ring-red-400' : ''
                }`}
                placeholder="Doe"
              />
              {errors.lastName && (
                <p className="text-red-400 text-xs mt-1 animate-pulse">{errors.lastName}</p>
              )}
            </div>
          </div>

          <div className="animate-slide-up" style={{ animationDelay: '0.1s' }}>
            <label htmlFor="email" className="block text-sm font-medium text-white/90 mb-2">
              Email Address
            </label>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-white/70 w-5 h-5" />
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                className={`input-glass w-full pl-10 pr-4 py-3 ${
                  errors.email ? 'border-red-400 focus:ring-red-400' : ''
                }`}
                placeholder="john@example.com"
              />
            </div>
            {errors.email && (
              <p className="text-red-400 text-sm mt-1 animate-pulse">{errors.email}</p>
            )}
          </div>

          <div className="animate-slide-up" style={{ animationDelay: '0.2s' }}>
            <label htmlFor="password" className="block text-sm font-medium text-white/90 mb-2">
              Password
            </label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-white/70 w-5 h-5" />
              <input
                type={showPassword ? 'text' : 'password'}
                id="password"
                name="password"
                value={formData.password}
                onChange={handleInputChange}
                className={`input-glass w-full pl-10 pr-12 py-3 ${
                  errors.password ? 'border-red-400 focus:ring-red-400' : ''
                }`}
                placeholder="Create a strong password"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-white/70 hover:text-white transition-colors"
              >
                {showPassword ? (
                  <EyeOff className="w-5 h-5" />
                ) : (
                  <Eye className="w-5 h-5" />
                )}
              </button>
            </div>
            {errors.password && (
              <p className="text-red-400 text-sm mt-1 animate-pulse">{errors.password}</p>
            )}
          </div>

          <div className="animate-slide-up" style={{ animationDelay: '0.3s' }}>
            <label htmlFor="confirmPassword" className="block text-sm font-medium text-white/90 mb-2">
              Confirm Password
            </label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-white/70 w-5 h-5" />
              <input
                type={showConfirmPassword ? 'text' : 'password'}
                id="confirmPassword"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleInputChange}
                className={`input-glass w-full pl-10 pr-12 py-3 ${
                  errors.confirmPassword ? 'border-red-400 focus:ring-red-400' : ''
                }`}
                placeholder="Confirm your password"
              />
              <button
                type="button"
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-white/70 hover:text-white transition-colors"
              >
                {showConfirmPassword ? (
                  <EyeOff className="w-5 h-5" />
                ) : (
                  <Eye className="w-5 h-5" />
                )}
              </button>
            </div>
            {errors.confirmPassword && (
              <p className="text-red-400 text-sm mt-1 animate-pulse">{errors.confirmPassword}</p>
            )}
          </div>

          <div className="flex items-start text-white/80">
            <input
              type="checkbox"
              className="w-4 h-4 text-green-400 bg-transparent border-white/30 rounded focus:ring-green-400 focus:ring-offset-0 mt-1"
            />
            <label className="ml-2 text-sm">
              I agree to the{' '}
              <button className="text-green-300 hover:text-green-200 transition-colors underline">
                Terms of Service
              </button>
              {' '}and{' '}
              <button className="text-green-300 hover:text-green-200 transition-colors underline">
                Privacy Policy
              </button>
            </label>
          </div>

          <button
            type="button"
            onClick={handleSubmit}
            disabled={isLoading}
            className="btn-gradient w-full animate-slide-up"
            style={{ animationDelay: '0.4s' }}
          >
            {isLoading ? (
              <div className="flex items-center justify-center">
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                Creating Account...
              </div>
            ) : (
              'Create Account'
            )}
          </button>
        </div>

        <div className="mt-6 flex items-center">
          <div className="flex-1 border-t border-white/20"></div>
          <span className="px-4 text-sm text-white/60">Or sign up with</span>
          <div className="flex-1 border-t border-white/20"></div>
        </div>

        <div className="mt-4">
          <button className="w-full flex items-center justify-center px-4 py-3 bg-white/10 backdrop-blur-sm border border-white/20 rounded-lg hover:bg-white/20 transition-all duration-200 text-white/90 hover:text-white">
            <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24">
              <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
              <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
              <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
              <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
            </svg>
            <span className="text-sm font-medium">Continue with Google</span>
          </button>
        </div>

        <p className="mt-6 text-center text-sm text-white/70">
          Already have an account?{' '}
          <button
            onClick={() => setCurrentPage('login')}
            className="text-green-300 hover:text-green-200 font-semibold transition-colors hover:underline"
          >
            Sign in here
          </button>
        </p>
      </div>
    </div>
  );
}
