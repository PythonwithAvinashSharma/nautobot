import requests
from bs4 import BeautifulSoup
import re
import time

def login_to_internal_platform(url="http://16.171.65.143/", username="admin", password="admin"):
    """
    Login to the Internal Developer Platform using requests
    
    Args:
        url (str): The base URL of the Internal Developer Platform
        username (str): Username for login
        password (str): Password for login
    
    Returns:
        requests.Session: Active session object after successful login
    """
    # Create a session to maintain cookies
    session = requests.Session()
    
    # Navigate to the base URL, which should redirect to login page
    try:
        print(f"Connecting to {url}...")
        response = session.get(url, timeout=10)
        current_url = response.url
        
        print(f"Current URL: {current_url}")
        
        # If not redirected to login page, manually go there
        if "/login/" not in current_url:
            login_url = f"{url.rstrip('/')}/login/?next=/"
            print(f"Navigating to login page: {login_url}")
            response = session.get(login_url, timeout=10)
            
        # Parse the page to find the CSRF token
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for CSRF token - common formats in Django
        csrf_token = None
        # Try to find it in the form
        csrf_input = soup.find('input', {'name': 'csrfmiddlewaretoken'})
        if csrf_input:
            csrf_token = csrf_input.get('value')
        else:
            # Try to find it in cookies
            csrf_token = session.cookies.get('csrftoken')
            if not csrf_token:
                # Look for it in the HTML as a variable
                csrf_pattern = re.compile(r"csrfToken['\"]?\s*[:=]\s*['\"]([^'\"]+)")
                match = csrf_pattern.search(response.text)
                if match:
                    csrf_token = match.group(1)
        
        if not csrf_token:
            print("WARNING: Could not find CSRF token. Login might fail.")
        else:
            print(f"Found CSRF token: {csrf_token[:5]}...{csrf_token[-5:]}")
            
        # Prepare login data
        login_data = {
            'username': username,
            'password': password
        }
        
        # Add CSRF token if found
        if csrf_token:
            login_data['csrfmiddlewaretoken'] = csrf_token
            
        # Set proper headers
        headers = {
            'Referer': response.url,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        if csrf_token:
            headers['X-CSRFToken'] = csrf_token
            
        # Submit the login form
        print(f"Submitting login form with username: {username}")
        login_response = session.post(
            response.url,
            data=login_data,
            headers=headers,
            allow_redirects=True,
            timeout=10
        )
        
        # Check if login was successful (usually redirect to dashboard)
        print(f"Response status: {login_response.status_code}")
        print(f"Redirected to: {login_response.url}")
        
        # Save the response for debugging
        with open("login_response.html", "w") as f:
            f.write(login_response.text)
            print("Saved response HTML to 'login_response.html' for debugging")
        
        # Basic check if login was successful
        if "/login/" not in login_response.url:
            print("Login appears successful (redirected away from login page)")
            
            # Check for password change popup in the response
            if "password change" in login_response.text.lower() or "password" in login_response.text.lower() and "breach" in login_response.text.lower():
                print("Password change popup detected in the response")
                
                # Look for the OK button's form or link
                popup_soup = BeautifulSoup(login_response.text, 'html.parser')
                ok_button = popup_soup.find('button', text=re.compile(r'OK', re.IGNORECASE))
                
                if ok_button:
                    # Find the form or determine the request needed to dismiss popup
                    popup_form = ok_button.find_parent('form')
                    if popup_form:
                        popup_action = popup_form.get('action', login_response.url)
                        popup_method = popup_form.get('method', 'post').lower()
                        popup_data = {}
                        
                        # Collect all form inputs
                        for input_tag in popup_form.find_all('input'):
                            name = input_tag.get('name')
                            value = input_tag.get('value', '')
                            if name:
                                popup_data[name] = value
                                
                        # Submit the form to dismiss popup
                        print(f"Submitting form to dismiss popup: {popup_action}")
                        if popup_method == 'post':
                            dismiss_response = session.post(
                                popup_action, 
                                data=popup_data,
                                headers={'Referer': login_response.url}
                            )
                        else:
                            dismiss_response = session.get(
                                popup_action,
                                params=popup_data,
                                headers={'Referer': login_response.url}
                            )
                        print(f"Popup dismiss response status: {dismiss_response.status_code}")
                else:
                    print("OK button not found in popup, might need to handle differently")
            
            print("Login process completed")
            return session
        else:
            print("Login appears to have failed (still on login page)")
            if "error" in login_response.text.lower():
                # Extract error message
                error_soup = BeautifulSoup(login_response.text, 'html.parser')
                error_elem = error_soup.find(class_=re.compile(r'error|alert|danger'))
                if error_elem:
                    print(f"Error message: {error_elem.get_text().strip()}")
                    
            return None
            
    except Exception as e:
        print(f"An error occurred during login: {str(e)}")
        return None
        
if __name__ == "__main__":
    # Run the login automation
    session = login_to_internal_platform()
    
    if session:
        print("\nLogin successful! Active session established.")
        print("\nTesting access to protected content...")
        
        # Test the session by accessing a protected page
        try:
            dashboard_url = "http://16.171.65.143/"
            response = session.get(dashboard_url)
            
            # Check if we got actual dashboard content
            if "login" not in response.url.lower():
                print(f"Successfully accessed: {dashboard_url}")
                
                # Look for expected dashboard elements
                if "key features" in response.text.lower() or "home" in response.text.lower():
                    print("Dashboard content verified!")
                else:
                    print("WARNING: Accessed page but couldn't verify dashboard content")
            else:
                print(f"FAILED: Redirected to login when accessing {dashboard_url}")
        except Exception as e:
            print(f"Error testing protected content: {e}")
    else:
        print("\nLogin failed. Please check credentials and URL.")