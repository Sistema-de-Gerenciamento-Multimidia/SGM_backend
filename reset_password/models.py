from django.db import models


class PasswordReset(models.Model):
    email = models.EmailField(max_length=100, unique=True)
    token = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now=True)
    
    def __repr__(self):
        return f"Password Rset - Email: {self.email}"
