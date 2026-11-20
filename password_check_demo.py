from backend_project import create_app
from backend_project.models import User
app = create_app("development")
with app.app_context():
    user = User.query.filter_by(email="hiker1@example.com").first()

    if user is None:
        print("No user found. Register hiker1@example.com first.")
    else:
        print("Correct password:", user.check_password("longenough"))
        print("Wrong password:", user.check_password("wrongpassword"))
