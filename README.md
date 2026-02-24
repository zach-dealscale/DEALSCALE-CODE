## Django Boilerplate Project

This is a **modular and extensible Django boilerplate** designed for quick and scalable application development. It includes support for optional REST APIs, a structured app layout, and environment-based configurations.

**Note:** This boilerplate is private and intended solely for Distack Solutions and its relevant people. It cannot be used for personal purposes or distributed without permission.


#### You are encouraged to setup via docker to avoid problems

---

## **Features**

- Modular app structure with separate directories for core and API apps.
- Support for Django REST Framework (conditionally enabled via `.env`).
- Secure and scalable settings structure with environment variables.
- Preconfigured static and media file handling.
- Authentication system with custom user model and Bootstrap 5 templates.
- Version-controlled `README` and `.gitignore` tailored for Django.
- Optional API setup for REST-enabled projects.
- Docker and Nginx setup for containerized deployments.

---

## **Project Structure**

```plaintext
project_root/
├── apps/
│   ├── core/                # Core app for non-auth features
│   ├── authentication/      # Authentication app with custom user model
│       ├── apis/            # API-related logic for authentication
│           ├── serializers.py
│           ├── views.py
│           ├── endpoints.py
├── config/
│   ├── settings/            # Modular settings
│       ├── base.py          # Base settings
│       ├── development.py   # Development-specific settings
│       ├── production.py    # Production-specific settings
├── static/                  # Static files
├── media/                   # Media files (user uploads)
├── templates/               # Shared templates
├── .env                     # Environment variables (ignored in git)
├── Dockerfile               # Docker configuration for the app
├── Dockerfile.nginx         # Docker configuration for Nginx
├── docker-compose.yml       # Docker Compose configuration
├── entrypoint.sh            # Entrypoint script for Docker
├── nginx.conf               # Nginx configuration file
├── manage.py                # Django CLI entry point
```

---

## **Getting Started**

### **Method 1: Docker-Compose Setup**

#### **1. Clone the Repository**

```bash
git clone <repository-url>
cd <repository-folder>
```

#### **2. Configure Environment Variables**

Create a `.env` file in the root directory:

```plaintext
# Environment
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,boiler.distack-solutions.com

# Database
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=db
DB_PORT=5432

# REST Framework
REST_ENABLED=True
```

#### **3. Build and Run Docker Containers**

```bash
docker-compose build
docker-compose up -d
```

#### **4. Apply Migrations**

Execute the migration commands inside the Django container:

```bash
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
```

#### **5. Access the Application**

Visit [http://localhost:8000](http://localhost:8000) or your configured domain in the `.env` file.

---

### **Method 2: Usual Setup**

#### **1. Clone the Repository**

```bash
git clone <repository-url>
cd <repository-folder>
```

#### **2. Set Up a Virtual Environment**

```bash
python -m venv env
source env/bin/activate  # For Windows: env\Scripts\activate
```

#### **3. Install Dependencies**

```bash
pip install -r requirements.txt
```

#### **4. Configure Environment Variables**

Create a `.env` file in the root directory:

```plaintext
# Environment
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=localhost
DB_PORT=5432

# REST Framework
REST_ENABLED=True  # Set to False to disable REST functionality
```

#### **5. Run Migrations**

```bash
python manage.py makemigrations
python manage.py migrate
```

#### **6. Run the Development Server**

```bash
python manage.py runserver
```

Visit [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.

---

## **Updating the Nginx Configuration for Custom Domain**

The default Nginx configuration (`nginx.conf`) is set to `boiler.distack-solutions.com`. Update it to your custom domain as follows:

1. Open `nginx.conf`:
   ```bash
   nano nginx.conf
   ```

2. Replace `boiler.distack-solutions.com` with your desired domain.

3. Restart the Docker containers:
   ```bash
   docker-compose down
   docker-compose up -d
   ```

---

## **REST API Setup (Optional)**

If `REST_ENABLED=True` in `.env`, REST-related apps and the Django REST Framework are enabled:

1. **API Example:**
   - User endpoints available at `/api/auth/`.
   - Example URLs:
     - `/api/auth/users/`: List all users.
     - `/api/auth/users/<id>/`: Retrieve a user by ID.

2. **API Directory Structure:**
   ```plaintext
   apps/authentication/apis/
   ├── serializers.py   # DRF serializers
   ├── views.py         # API views
   ├── endpoints.py     # URL routing for APIs
   ```

3. **Disable APIs:**
   - Set `REST_ENABLED=False` in `.env`.
   - Remove `api/` folder if not required.

---

## **Static and Media Files**

### **Static Files**

- Place CSS, JS, and images in the `static/` directory.
- Collected in `staticfiles/` for production using:
  ```bash
  python manage.py collectstatic
  ```

### **Media Files**

- User uploads are stored in the `media/` directory.
- Ensure `media/` is writable in production.

---

## **Authentication**

- Custom user model with email as the primary identifier.
- Authentication endpoints for login, signup, and password management.
- Fully styled with Bootstrap 5.

---

## **Environment Variables**

### **.env Example:**

```plaintext
# Environment
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=localhost
DB_PORT=5432

# REST Framework
REST_ENABLED=True
```

### **Secure Your `.env`**

- Do not commit the `.env` file to version control.
- Add `.env` to `.gitignore`:
  ```plaintext
  .env
  ```

---

## **Deployment**

### **1. Build Docker Containers**

```bash
docker-compose build
```

### **2. Run Docker Containers**

```bash
docker-compose up -d
```

### **3. Collect Static Files**

```bash
python manage.py collectstatic
```

### **4. Apply Migrations**

```bash
python manage.py migrate
```

### **5. Use a WSGI/ASGI Server**

- Configure Gunicorn, uWSGI, or Daphne for production.
- Example with Gunicorn:
  ```bash
  gunicorn config.wsgi:application --bind 0.0.0.0:8000
  ```

Note: use 'docker-compose exec web bash' to run django specific commands while docker is running
where **web** is the name of the django service
---

## **Contributing**

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature-branch-name`).
3. Commit your changes (`git commit -m 'Add feature'`).
4. Push to the branch (`git push origin feature-branch-name`).
5. Open a pull request.

**Note: When you plan to use any third party package Do following before starting:**
- Discuss with the team lead in your project discord channel with need, reason and benefits
- If approved, add it first in the requirements.txt file with the most stable version
- Add a explaining the addition of the package with reason
- Start using the package in the code
---

## **License**

This project is licensed under the MIT License. See the LICENSE file for details.

---

## **Contact**

For questions or feedback, please reach out to contact@distack-solutions.com.

