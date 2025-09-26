# 🎓 Educational Management System USING DOCKER 

A comprehensive web-based educational management platform designed to streamline academic operations for educational institutions. This system provides robust features for student management, examination handling, result processing, attendance tracking, and secure payment processing.

## ✨ Features

### 👥 User Management
- **Student Registration**: Complete student onboarding with profile management
- **Teacher Registration**: Faculty registration with role-based access controls
- **Multi-role Authentication**: Secure login system for students, teachers, and administrators

### 📝 Examination System
- **Exam Registration**: Seamless exam enrollment process for students
- **Dynamic Exam Management**: Teachers can create, schedule, and manage examinations
- **Automated Notifications**: Real-time exam alerts and updates
- **Result Processing**: Comprehensive result management with grade calculations

### 📊 Academic Tracking
- **Result Display**: Detailed result presentation on student profile pages
- **Grade Analytics**: Performance tracking and trend analysis
- **Attendance Management**: Real-time attendance tracking and reporting
- **Academic Progress**: Comprehensive academic performance monitoring

### 💳 Payment Integration
- **Razorpay Integration**: Secure payment gateway for examination fees
- **Transaction Management**: Complete payment history and receipt generation
- **Fee Structure**: Flexible fee management for different examination types
- **Payment Notifications**: Automated payment confirmation and reminders
-  **With automatic ADMIT CARD generation ost payment. **

### 🔔 Notification System
- **Exam Alerts**: Timely notifications for upcoming examinations
- **Result Announcements**: Instant result publication notifications
- **Attendance Alerts**: Automated attendance-related notifications
- **System Updates**: Important announcements and updates

## 🚀 Getting Started

### Prerequisites
- Python (v3.8 or higher)
- Django (v4.0 or higher)
- SQLite/PostgreSQL/MySQL
- Razorpay Account (for payment processing)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/educational-management-system.git
   cd educational-management-system
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   Create a `.env` file in the root directory:
   ```env
   DEBUG=True
   SECRET_KEY=your_django_secret_key
   DATABASE_URL=sqlite:///db.sqlite3
   RAZORPAY_KEY_ID=your_razorpay_key_id
   RAZORPAY_KEY_SECRET=your_razorpay_key_secret
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_HOST_USER=your_email@gmail.com
   EMAIL_HOST_PASSWORD=your_email_password
   EMAIL_USE_TLS=True
   ```

5. **Database Migration**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create Superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start the development server**
   ```bash
   python manage.py runserver
   ```

8. **Access the application**
   Open your browser and navigate to `http://localhost:8000`

## 🏗️ System Architecture

### Database Models (Django)

#### Student Model
```python
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    student_id = models.CharField(max_length=20, unique=True)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    enrollment_date = models.DateTimeField(auto_now_add=True)
    # Additional fields...
```

#### Teacher Model
```python
class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    teacher_id = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=100)
    subjects = models.ManyToManyField('Subject')
    # Additional fields...
```

#### Exam Model
```python
class Exam(models.Model):
    name = models.CharField(max_length=200)
    subject = models.ForeignKey('Subject', on_delete=models.CASCADE)
    date = models.DateTimeField()
    duration = models.DurationField()
    total_marks = models.IntegerField()
    # Additional fields...
```

#### Result Model
```python
class Result(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    marks_obtained = models.IntegerField()
    grade = models.CharField(max_length=2)
    created_at = models.DateTimeField(auto_now_add=True)
    # Additional fields...
```

#### Attendance Model
```python
class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey('Subject', on_delete=models.CASCADE)
    date = models.DateField()
    is_present = models.BooleanField(default=False)
    # Additional fields...
```

#### Payment Model
```python
class Payment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    razorpay_order_id = models.CharField(max_length=100)
    razorpay_payment_id = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    # Additional fields...
```

## 📱 User Interfaces

### Student Dashboard
- Personal profile management
- Exam registration portal
- Result viewing interface
- Attendance tracking
- Payment history
- Notification center

### Teacher Dashboard
- Student management
- Exam creation and management
- Result entry system
- Attendance marking
- Performance analytics

### Admin Panel
- System configuration
- User management
- Payment monitoring
- Report generation
- Notification management

## 🔐 Security Features

- **Django Authentication**: Built-in user authentication system
- **CSRF Protection**: Cross-site request forgery protection
- **Session Security**: Secure session management
- **Password Hashing**: Secure password storage
- **Permission Decorators**: View-level access control
- **Secure Payments**: PCI-compliant Razorpay integration
- **Input Validation**: Django form validation and sanitization

## 💻 Technology Stack

### Backend
- **Django**: Python web framework
- **Django ORM**: Database abstraction layer
- **SQLite/PostgreSQL**: Database management
- **Django Authentication**: Built-in user management
- **Django Sessions**: Session management

### Frontend
- **HTML5**: Markup language
- **CSS3**: Styling and responsive design
- **JavaScript**: Client-side interactivity
- **Bootstrap** (optional): CSS framework

### Integrations
- **Razorpay**: Payment gateway integration
- **Django Email**: Email notifications

## 📊 Django URLs & Views

### URL Configuration
```python
# urls.py
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('student/register/', views.student_register, name='student_register'),
    path('teacher/register/', views.teacher_register, name='teacher_register'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('exams/', views.exam_list, name='exam_list'),
    path('exam/register/<int:exam_id>/', views.exam_register, name='exam_register'),
    path('results/', views.student_results, name='student_results'),
    path('attendance/', views.attendance_view, name='attendance'),
    path('payment/', views.payment_view, name='payment'),
    path('payment/success/', views.payment_success, name='payment_success'),
]
```

### Key Views
- **Authentication Views**: Login, logout, registration
- **Student Views**: Dashboard, profile, exam registration
- **Teacher Views**: Dashboard, result entry, attendance marking
- **Exam Views**: List, registration, management
- **Payment Views**: Razorpay integration, success/failure handling

## 🧪 Testing

Run the Django test suite:
```bash
python manage.py test
```

Run specific app tests:
```bash
python manage.py test students
python manage.py test exams
```



## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request





---

**Made with ❤️ for Education**
