## To see only the currently installed Python versions using pyenv, run:

```
pyenv versions
```

This will list all Python versions installed via pyenv. The currently active version will be marked with an asterisk (*).
pyenv versions



pyenv local 3.9.21

This repo uses the Python 3.9.21

### Steps to Create a Local Python Environment

1. **Install the Desired Python Version**:
   - List available Python versions:
     ```powershell
     pyenv install --list
     ```
   - Install a specific Python version (e.g., 3.12.0):
     ```powershell
     pyenv install 3.12.0
     ```

2. **Set the Local Python Version for Your Project**:
   - Navigate to your project directory:
     ```powershell
     cd path\to\your\django\project
     ```
   - Set the local Python version:
     ```powershell
     pyenv local 3.12.0
     ```

3. **Create a Virtual Environment**:
   - Create a virtual environment using the specified Python version:
     ```powershell
     python -m venv venv
     ```

4. **Activate the Virtual Environment**:
   - On Windows:
     ```powershell
     venv\Scripts\activate
     ```
   - On macOS and Linux:
     ```sh
     source venv/bin/activate
     ```

5. **Install Dependencies from `requirements.txt`**:
   ```powershell
   pip3 install -r requirements.txt
   ```

## EMail Account Notes

You are getting this error because **Google no longer allows normal passwords for SMTP** if you have 2-Step Verification enabled on your Gmail account.  
You must use an **App Password** instead of your regular Gmail password.

---

### How to fix

1. **Enable 2-Step Verification** on your Google account if you haven't already:  
   https://myaccount.google.com/security

2. **Generate an App Password**:  
   - Go to: https://myaccount.google.com/apppasswords  
   - Select "Mail" as the app and "Other" (or your device) as the device.
   - Google will generate a 16-character password.  
   - Use this password in your config.ini as `sender_password`.

3. **Update your config.ini** with the new app password.

---

**References:**  
- [Google: Sign in using App Passwords](https://support.google.com/mail/?p=InvalidSecondFactor)

---

**Summary:**  
Replace your Gmail password with an App Password in your configuration.  
This is required for all programmatic access to Gmail SMTP.