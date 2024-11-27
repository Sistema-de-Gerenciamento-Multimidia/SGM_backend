from django.contrib.auth.base_user import BaseUserManager


class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email and username are the identifiers for authentication
    """
    def create_user(self, email, username, password, **extra_fields):
        """
        Create and save a user with the given email, username and password.
        """
        if not email:
            raise ValueError("Email is required.")
        if not username:
            raise ValueError("Username is required.")
        if not password:
            raise ValueError("Password is required.")

        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save() # (using='test_external_db)

        return user
    
    def create_superuser(self, email, username, password, **extra_fields):
        """
        Create and save a SuperUser with the given email, username and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        
        if extra_fields.get("is_staff") is not True:
            raise ValueError(("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(("Superuser must have is_superuser=True."))
        
        return self.create_user(email, username, password, **extra_fields)
