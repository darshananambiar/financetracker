from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Q
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
from .models import Transaction, Category, Budget
from django.http import JsonResponse
from django.forms.models import model_to_dict
from .forms import TransactionForm, CategoryForm, BudgetForm


@login_required
def dashboard(request):
    # Get current month transactions
    current_month = timezone.now().date().replace(day=1)
    next_month = (current_month.replace(day=28) + timedelta(days=4)).replace(day=1)
    
    # Calculate totals
    total_income = Transaction.objects.filter(
        user=request.user,
        type='income',
        date__gte=current_month,
        date__lt=next_month
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    
    total_expenses = Transaction.objects.filter(
        user=request.user,
        type='expense',
        date__gte=current_month,
        date__lt=next_month
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    
    balance = total_income - total_expenses
    
    # Recent transactions
    recent_transactions = Transaction.objects.filter(
        user=request.user
    ).order_by('-date', '-created_at')[:10]
    
    # Budget overview
    budgets = Budget.objects.filter(
        user=request.user,
        month=current_month
    )
    
    context = {
        'total_income': total_income,
        'total_expenses': total_expenses,
        'balance': balance,
        'recent_transactions': recent_transactions,
        'budgets': budgets,
        'current_month': current_month,
    }
    
    return render(request, 'tracker/dashboard.html', context)


@login_required
def add_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST, user=request.user)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            messages.success(request, 'Transaction added successfully!')
            return redirect('dashboard')
    else:
        form = TransactionForm(user=request.user)
    
    return render(request, 'tracker/add_transaction.html', {'form': form})


@login_required
def transaction_list(request):
    transactions = Transaction.objects.filter(user=request.user)
    
    # Filter by type
    transaction_type = request.GET.get('type')
    if transaction_type in ['income', 'expense']:
        transactions = transactions.filter(type=transaction_type)
    
    # Filter by category
    category_id = request.GET.get('category')
    if category_id:
        transactions = transactions.filter(category_id=category_id)
    
    # Filter by date range
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    if date_from:
        transactions = transactions.filter(date__gte=date_from)
    if date_to:
        transactions = transactions.filter(date__lte=date_to)
    
    categories = Category.objects.filter(user=request.user)
    
    context = {
        'transactions': transactions,
        'categories': categories,
        'selected_type': transaction_type,
        'selected_category': category_id,
        'date_from': date_from,
        'date_to': date_to,
    }
    
    return render(request, 'tracker/transaction_list.html', context)


@login_required
def edit_transaction(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=transaction, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Transaction updated successfully!')
            return redirect('transaction_list')
    else:
        form = TransactionForm(instance=transaction, user=request.user)
    
    return render(request, 'tracker/edit_transaction.html', {'form': form, 'transaction': transaction})


@login_required
def delete_transaction(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    
    if request.method == 'POST':
        transaction.delete()
        messages.success(request, 'Transaction deleted successfully!')
        return redirect('transaction_list')
    
    return render(request, 'tracker/delete_transaction.html', {'transaction': transaction})


@login_required
def category_list(request):
    categories = Category.objects.filter(user=request.user)
    return render(request, 'tracker/category_list.html', {'categories': categories})


@login_required
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            messages.success(request, 'Category added successfully!')
            return redirect('category_list')
    else:
        form = CategoryForm()
    
    return render(request, 'tracker/add_category.html', {'form': form})


@login_required
def budget_list(request):
    budgets = Budget.objects.filter(user=request.user).order_by('-month')
    return render(request, 'tracker/budget_list.html', {'budgets': budgets})


@login_required
def add_budget(request):
    if request.method == 'POST':
        form = BudgetForm(request.POST, user=request.user)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.user = request.user
            budget.save()
            messages.success(request, 'Budget added successfully!')
            return redirect('budget_list')
    else:
        form = BudgetForm(user=request.user)
    
    return render(request, 'tracker/add_budget.html', {'form': form})


@login_required
def get_categories_by_type(request):
    transaction_type = request.GET.get('type')
    categories = Category.objects.filter(user=request.user, type=transaction_type).values('id', 'name')
    return JsonResponse(list(categories), safe=False)