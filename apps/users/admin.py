from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin
from unfold.decorators import action, display
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm

from apps.users.models import User


class CustomUserCreationForm(UserCreationForm):
    """Clean user creation form in Django Admin."""

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'lives')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['lives'].initial = 5
        self.fields['email'].required = False


class CustomUserChangeForm(UserChangeForm):
    """Clean user modification form in Django Admin with clear password change action."""

    class Meta(UserChangeForm.Meta):
        model = User
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'password' in self.fields:
            self.fields['password'].help_text = format_html(
                '<div class="mt-2 flex flex-col gap-1.5">'
                '<a href="../password/" class="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-full text-xs font-semibold bg-primary-600 hover:bg-primary-700 text-white transition-all shadow-xs w-fit">'
                '<span class="material-symbols-outlined text-xs">key</span>'
                '<span>Сменить пароль игрока</span>'
                '</a>'
                '<span class="text-xs text-font-subtle-light dark:text-font-subtle-dark">'
                'Пароли хранятся в хэшированном виде (PBKDF2 SHA256). Для изменения пароля нажмите кнопку выше.'
                '</span>'
                '</div>'
            )


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    """
    Modern Google Material You (M3) Admin interface for Player management.
    Includes full password change capabilities, clean architecture, and gameplay tools.
    """
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    change_password_form = AdminPasswordChangeForm

    actions_detail = ['change_password_action']
    actions_row = ['change_password_action']

    list_display = (
        'id',
        'username',
        'email_display',
        'lives_badge',
        'password_action_button',
        'is_active',
        'is_staff',
        'created_at_display',
    )
    list_display_links = ('id', 'username')
    list_filter = (
        'is_active',
        'is_staff',
        'is_superuser',
        ('created_at', admin.DateFieldListFilter),
    )
    search_fields = ('id', 'username', 'email')
    ordering = ('-created_at',)
    readonly_fields = ('id', 'created_at', 'last_login', 'date_joined')

    # Grouped fields for existing user details
    fieldsets = (
        (
            _('Учетные данные игрока'),
            {
                'fields': ('username', 'password'),
                'description': 'Имя пользователя и защищенный пароль игрока.',
            },
        ),
        (
            _('Игровой профиль и жизни'),
            {
                'fields': ('email', 'lives'),
                'description': 'Количество жизней игрока (>= 0) и email (опционально).',
            },
        ),
        (
            _('Статус и права доступа'),
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'groups',
                    'user_permissions',
                ),
                'classes': ('collapse',),
            },
        ),
        (
            _('История и метаданные'),
            {
                'fields': ('id', 'created_at', 'last_login', 'date_joined'),
                'classes': ('collapse',),
            },
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': ('username', 'email', 'lives', 'password1', 'password2'),
            },
        ),
    )

    actions = [
        'action_reset_lives_to_default',
        'action_add_one_life',
        'action_set_lives_to_zero',
    ]

    # Action to redirect directly to player password change form
    @action(description='Сменить пароль', icon='key')
    def change_password_action(self, request, object_id: int):
        return redirect(reverse('admin:auth_user_password_change', args=[object_id]))

    @display(description='Email', ordering='email')
    def email_display(self, obj: User) -> str:
        """Display placeholder if email is empty."""
        return obj.email if obj.email else format_html('<span class="text-gray-400 dark:text-gray-500">—</span>')

    @display(description='Жизни', ordering='lives')
    def lives_badge(self, obj: User):
        """Visual Google Pill badge for player lives."""
        if obj.lives >= 5:
            badge_classes = "bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300 border-emerald-300 dark:border-emerald-800"
            icon = "favorite"
        elif obj.lives > 0:
            badge_classes = "bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300 border-amber-300 dark:border-amber-800"
            icon = "favorite_border"
        else:
            badge_classes = "bg-rose-100 text-rose-800 dark:bg-rose-950 dark:text-rose-300 border-rose-300 dark:border-rose-800"
            icon = "heart_broken"

        return format_html(
            '<span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold border {}">'
            '<span class="material-symbols-outlined text-xs leading-none">{}</span>'
            '<span>{} жизней</span>'
            '</span>',
            badge_classes,
            icon,
            obj.lives,
        )

    @display(description='Пароль')
    def password_action_button(self, obj: User):
        """Quick button in list view to change player's password."""
        url = reverse('admin:auth_user_password_change', args=[obj.pk])
        return format_html(
            '<a href="{}" class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium bg-base-100 hover:bg-base-200 dark:bg-base-800 dark:hover:bg-base-700 text-font-important-light dark:text-font-important-dark border border-base-200 dark:border-base-700 transition-all shadow-xs" title="Сменить пароль игрока">'
            '<span class="material-symbols-outlined text-xs">key</span>'
            '<span>Сменить пароль</span>'
            '</a>',
            url
        )

    @display(description='Регистрация', ordering='created_at')
    def created_at_display(self, obj: User) -> str:
        return obj.created_at.strftime('%d.%m.%Y %H:%M')

    # Admin actions for game masters
    @action(description='Сбросить жизни выбранных игроков на 5 (по умолчанию)')
    def action_reset_lives_to_default(self, request, queryset):
        updated_count = queryset.update(lives=5)
        self.message_user(
            request,
            f"Успешно сброшены жизни на 5 для {updated_count} игроков.",
            level=messages.SUCCESS
        )

    @action(description='Добавить +1 жизнь выбранным игрокам')
    def action_add_one_life(self, request, queryset):
        for user in queryset:
            user.lives += 1
            user.save(update_fields=['lives'])
        self.message_user(
            request,
            f"Успешно добавлена 1 жизнь для {queryset.count()} игроков.",
            level=messages.SUCCESS
        )

    @action(description='Обнулить жизни выбранным игрокам (0 - Game Over)')
    def action_set_lives_to_zero(self, request, queryset):
        updated_count = queryset.update(lives=0)
        self.message_user(
            request,
            f"Установлено 0 жизней для {updated_count} игроков.",
            level=messages.WARNING
        )
