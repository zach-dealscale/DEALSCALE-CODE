# test_salesforce_oauth.py

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')  # change this
django.setup()

from django.test import RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from apps.salesforce.utils.salesforce_oauth import SalesforceOAuth  
import urllib.parse


def test_salesforce_pkce_flow():
    # Step 1: Simulate request + session
    factory = RequestFactory()
    request = factory.get('/')
    middleware = SessionMiddleware(lambda r: None)
    middleware.process_request(request)
    request.session.save()

    # Step 2: Start OAuth flow
    oauth = SalesforceOAuth(session=request.session)
    auth_url = oauth.get_authorization_url(prompt_consent=True)




    
    print("\n🔗 Step 1: Visit this URL to authorize:")
    print(auth_url)

    print("\n🚨 After authorization, you'll be redirected to:")
    print("   http://localhost:8000/salesforce/callback/?code=XXXX\n")

    # Step 3: Enter the code
    code = input("📥 Paste the ?code= from the URL here: ").strip()

    # Step 4: Fetch token using the same session
    oauth = SalesforceOAuth(session=request.session)
    try:
        main_code = urllib.parse.unquote(code)
        print("main_code: ", main_code)
        token_data = oauth.fetch_token(main_code)
        print("\n✅ Access Token Response:")
        for k, v in token_data.items():
            print(f"{k}: {v}")

        if 'refresh_token' in token_data:
            print("\n♻️ Testing refresh...")
            refreshed = oauth.refresh_access_token(token_data['refresh_token'])
            print("✅ Refreshed Access Token:")
            print(refreshed)

    except Exception as e:
        print("\n❌ Error occurred during token exchange:")
        print(str(e))


if __name__ == "__main__":
    test_salesforce_pkce_flow()
