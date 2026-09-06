from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models


class User(AbstractUser):
    """
    Custom User model for Unity WebGL players and system administrators.
    Stores player credentials, optional email, lives, and creation timestamp.
    """
    email = models.EmailField(
        blank=True,
        default='',
        verbose_name='Email address'
    )
    lives = models.IntegerField(
        default=5,
        validators=[MinValueValidator(0)],
        verbose_name='Player lives',
        help_text='Current number of lives the player possesses (>= 0).'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created at'
    )

    class Meta:
        verbose_name = 'Игрок'
        verbose_name_plural = 'Игроки'
        ordering = ['-created_at']

    def clean(self):
        super().clean()
        if self.lives is not None and self.lives < 0:
            raise ValidationError({'lives': 'Lives cannot be negative.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def update_lives(self, new_lives: int) -> int:
        """Domain method to update player's lives with validation."""
        if new_lives < 0:
            raise ValidationError({'lives': 'Lives cannot be negative.'})
        self.lives = new_lives
        self.save(update_fields=['lives'])
        return self.lives

    def __str__(self):
        return f"{self.username} (ID: {self.id}, Lives: {self.lives})"
