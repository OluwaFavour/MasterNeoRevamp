from django.contrib.auth.models import BaseUserManager


class CompanyManager(BaseUserManager):
    """
    A custom manager for the Company model.
    """

    def create_user(self, email, password=None, **extra_fields):
        """
        Creates and saves a new user with the given email and password.

        Args:
            email (str): The email address of the user.
            password (str, optional): The password for the user. Defaults to None.
            **extra_fields: Additional fields to be saved in the user model.

        Returns:
            User: The newly created user.
        """
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Creates and saves a new superuser with the given email and password.

        Args:
            email (str): The email address of the superuser.
            password (str, optional): The password for the superuser. Defaults to None.
            **extra_fields: Additional fields to be saved in the superuser model.

        Returns:
            User: The newly created superuser.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)
