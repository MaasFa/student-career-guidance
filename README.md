    # Student Career Guidance & Personalized Roadmap Recommendation System

    A Django-based web application designed to help students explore career opportunities, access structured learning roadmaps, connect with mentors, and receive personalized career guidance through mentoring sessions.

    ## Overview

    The **Student Career Guidance System** provides a centralized platform where students can explore career paths, follow structured learning roadmaps, interact with experienced mentors, attend online lectures and workshops, and seek guidance regarding their career goals.

    The platform supports two user roles — Students and Mentors — with separate dashboards and functionalities to facilitate career exploration, mentorship, and learning.

    ## Key Features

    ### 1. User Authentication & Role Management
    - Student and Mentor registration.
    - Secure login and logout functionality.
    - Role-based dashboard redirection.
    - Separate student and mentor experiences.

    ### 2. Student Dashboard
    - Access a personalized student dashboard.
    - View published lectures and workshops.
    - Explore available mentors.
    - View confirmed mentoring sessions.
    - Access career roadmaps.
    - Submit career-related queries.

    ### 3. Student Profile Management
    - Update personal information.
    - Add educational qualifications.
    - Specify career interests.
    - Add technical skills and personal bio.
    - Upload profile pictures.

    ### 4. Mentor Management
    - Browse available mentors.
    - View mentor profiles and areas of expertise.
    - Access mentor experience and professional information.
    - Update mentor profiles.
    - Manage mentoring availability.

    ### 5. Mentor Session Booking
    - Mentors can publish their available time slots.
    - Students can explore mentor availability.
    - Students can request mentoring sessions.
    - Mentors can accept student queries and offer sessions.
    - Mentors can schedule sessions by providing date, time, and meeting links.
    - Students and mentors can view their scheduled sessions.

    ### 6. Student Query Management
    - Students can submit career-related queries.
    - Mentors can view open student queries.
    - Mentors can accept queries and offer personalized sessions.
    - Query status tracking: Open, Accepted, Scheduled, Resolved, and Closed.

    ### 7. Lectures & Workshops
    - Mentors can publish online lectures and workshops.
    - Add session title, topic, description, date, time, and duration.
    - Include online meeting links.
    - Students can explore published learning sessions.
    - Mentors can manage their published sessions.

    ### 8. Career Roadmap
    - Explore predefined career roadmaps across different categories.
    - Career categories include IT & Software, Data Science & AI, Core Engineering, Design, and Other.
    - View career overviews and suitable educational backgrounds.
    - Access structured roadmap stages.
    - Explore skills, learning durations, and recommended resources for each stage.
    - Roadmaps are managed through the application's database and can be published for students.

    ## Technology Stack

    | Category | Technologies |
    |---|---|
    | Backend | Python, Django |
    | Frontend | HTML5, CSS3, JavaScript |
    | Database | SQLite |
    | Authentication | Django Authentication System |
    | Image Handling | Pillow |
    | Environment Management | Python-dotenv |
    | Version Control | Git, GitHub |

    ## Project Structure

    ```text
    student-career-guidance/
    │
    ├── accounts/
    │   ├── models.py
    │   ├── views.py
    │   ├── forms.py
    │   └── urls.py
    │
    ├── mentors/
    │   ├── models.py
    │   ├── views.py
    │   ├── forms.py
    │   └── urls.py
    │
    ├── workshops/
    │   ├── models.py
    │   ├── views.py
    │   ├── forms.py
    │   └── urls.py
    │
    ├── queries/
    │   ├── models.py
    │   ├── views.py
    │   ├── forms.py
    │   └── urls.py
    │
    ├── roadmaps/
    │   ├── models.py
    │   ├── views.py
    │   └── urls.py
    │
    ├── config/
    │   ├── settings.py
    │   ├── urls.py
    │   ├── asgi.py
    │   └── wsgi.py
    │
    ├── templates/
    ├── static/
    │   └── css/
    │
    ├── manage.py
    ├── requirements.txt
    └── .gitignore
    ```


student-career-guidance/
│
├── accounts/
├── mentors/
├── workshops/
├── queries/
├── roadmaps/
│
├── skills/
│   ├── models.py
│   ├── views.py
│   └── services.py
│
├── skill_analysis/
│   ├── models.py
│   ├── views.py
│   └── services.py
│       └── gap_analyzer.py
│
├── recommendations/
│   ├── models.py
│   ├── views.py
│   └── services.py
│       └── recommendation_engine.py
│
├── progress/
│   ├── models.py
│   ├── views.py
│   └── services.py
│
├── ai_guidance/
│   ├── models.py
│   ├── views.py
│   ├── services/
│   └── prompts/
│
├── resources/
│   ├── models.py
│   └── views.py
│
├── notifications/
│   ├── models.py
│   ├── views.py
│   └── services.py
│
├── config/
├── templates/
├── static/
└── manage.py
    ## Installation & Setup

    Follow these steps to run the project locally.

    ### 1. Clone the Repository

    ```bash
    git clone https://github.com/MaasFa/student-career-guidance.git
    ```

    ### 2. Navigate to the Project Directory

    ```bash
    cd student-career-guidance
    ```

    ### 3. Create a Virtual Environment

    ```bash
    python -m venv venv
    ```

    Activate the virtual environment:

    **Windows:**
    ```bash
    venv\Scripts\activate
    ```

    **Linux / macOS:**
    ```bash
    source venv/bin/activate
    ```

    ### 4. Install Dependencies

    ```bash
    pip install -r requirements.txt
    ```

    ### 5. Apply Database Migrations

    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

    ### 6. Create a Superuser

    ```bash
    python manage.py createsuperuser
    ```

    ### 7. Run the Development Server

    ```bash
    python manage.py runserver
    ```

    Open the application in your browser:

    http://127.0.0.1:8000/

    ## Application Modules

    | Module | Responsibility |
    |---|---|
    | Accounts | Registration, authentication, profiles and dashboards |
    | Mentors | Mentor profiles, availability and session management |
    | Queries | Student queries and personalized mentoring sessions |
    | Workshops | Online lectures and workshops |
    | Roadmaps | Predefined career paths and structured learning stages |

    ## Future Enhancements

    - Skill gap analysis based on students' existing skills and career interests.
    - Personalized career roadmap recommendations.
    - Progress tracking for individual roadmap stages.
    - AI-powered career guidance and recommendations.
    - Integration of additional learning resources.
    - Notification system for mentoring sessions and workshops.

    ## Project Objective

    The primary objective of this project is to make career guidance more accessible to students by combining structured career roadmaps, mentor interaction, and online learning opportunities within a single platform.

    **License:** This project is developed for academic and educational purposes.