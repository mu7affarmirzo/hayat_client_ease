from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class MyAccountManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        if not email:
            raise ValueError("Users must have email")
        if not username:
            raise ValueError("Users must have username")

        user = self.model(
            email=self.normalize_email(email),
            username=username,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password):
        user = self.create_user(
            email=self.normalize_email(email),
            password=password,
            username=username,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class Account(AbstractBaseUser):
    email = models.EmailField(verbose_name="email", max_length=60, unique=True)
    username = models.CharField(max_length=30, unique=True)
    f_name = models.CharField(max_length=50, null=True)
    l_name = models.CharField(max_length=50, null=True)
    m_name = models.CharField(max_length=50, null=True)
    phone_number = models.CharField(max_length=30, null=True)
    tg_username = models.CharField(max_length=255, null=True, blank=True)
    sex = models.BooleanField(default=True)
    date_joined = models.DateTimeField(verbose_name='date joined', auto_now_add=True)
    last_login = models.DateTimeField(verbose_name='last login', auto_now=True)

    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_therapist = models.BooleanField(default=False)

    rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name="Ставка Массажиста (%)"
    )

    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = MyAccountManager()

    def __str__(self):
        return self.email

    # For checking permissions. to keep it simple all admin have ALL permissons
    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return self.is_admin

    @property
    def full_name(self):
        try:
            m_name = self.m_name
        except:
            m_name = ''

        return f"{self.f_name} {self.l_name} {m_name}"


class RolesModel(models.Model):
    name = models.CharField(max_length=50, unique=True)
    code = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class AccountRoleModel(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='roles', null=True, blank=True)
    role = models.ForeignKey(RolesModel, on_delete=models.CASCADE, related_name='accounts', null=True, blank=True)

    def __str__(self):
        return f"{self.account} {self.role}"


class TherapistModel(models.Model):
    f_name = models.CharField(max_length=50, null=True)
    l_name = models.CharField(max_length=50, null=True)
    m_name = models.CharField(max_length=50, null=True)
    phone_number = models.CharField(max_length=30, null=True)

    sex = models.BooleanField(default=True)

    rate = models.IntegerField(
        default=15,
        verbose_name="Ставка Массажиста (%)"
    )

    def __str__(self):
        try:
            m_name = self.m_name
        except:
            m_name = ''

        return f"{self.f_name} {self.l_name} {m_name}"

    @property
    def full_name(self):
        try:
            m_name = self.m_name
        except:
            m_name = ''

        return f"{self.f_name} {self.l_name} {m_name}"
