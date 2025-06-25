from django.contrib import admin
from .models import Category, Transaction, Budget


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'user', 'created_at']
    list_filter = ['type', 'created_at']
    search_fields = ['name', 'user__email']
    ordering = ['name']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['description', 'amount', 'type', 'category', 'user', 'date']
    list_filter = ['type', 'category', 'date', 'created_at']
    search_fields = ['description', 'user__email', 'category__name']
    ordering = ['-date', '-created_at']
    date_hierarchy = 'date'


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ['category', 'amount', 'month', 'user', 'spent_amount', 'remaining_amount']
    list_filter = ['month', 'category__type']
    search_fields = ['category__name', 'user__email']
    ordering = ['-month']
    
    def spent_amount(self, obj):
        return obj.spent_amount()
    spent_amount.short_description = 'Spent'
    
    def remaining_amount(self, obj):
        return obj.remaining_amount()
    remaining_amount.short_description = 'Remaining'