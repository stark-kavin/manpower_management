from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from .models import Center, Operator
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            auth_login(request, user)
            return redirect('home')
        else:
            return render(request, 'login.html', {'error': 'Invalid username or password. Please try again.'})
    
    return render(request, 'login.html')

def logout(request):
    auth_logout(request)
    return redirect('login')

def index(request):
    if not request.user.is_authenticated:
        return redirect('login')

    centers_count = Center.objects.count()
    operators_count = Operator.objects.count()
    creators_count = User.objects.count()
    
    context = {
        'centers_count': centers_count,
        'operators_count': operators_count,
        'creators_count': creators_count,
    }
    
    return render(request, 'home.html', context)

def centers(request):
    if not request.user.is_authenticated:
        return redirect('login')

    centers = Center.objects.all()
    
    # Add capacity percentage for each center
    centers_data = []
    for center in centers:
        operator_count = center.operators.count()
        capacity_percentage = int((operator_count / center.count) * 100) if center.count > 0 else 0
        centers_data.append({
            'center': center,
            'operator_count': operator_count,
            'capacity_percentage': capacity_percentage,
            'available_slots': center.count - operator_count
        })
    
    context = {
        'centers': centers,
        'centers_data': centers_data
    }
    
    return render(request, 'centers.html', context)

def center_detail(request, center_id):
    if not request.user.is_authenticated:
        return render(request, 'login.html')
    
    # Get the center object or return 404 if not found
    center = get_object_or_404(Center, id=center_id)
    
    # Get operators assigned to this center
    operators = center.operators.all()
    
    # Get all operators - both assigned and unassigned
    all_operators = Operator.objects.all()
    
    # Get operators that are not assigned to any center
    available_operators = Operator.objects.filter(center__isnull=True)
    
    context = {
        'center': center,
        'operators': operators,
        'available_operators': available_operators,
        'all_operators': all_operators,
        'operator_count': operators.count(),
        'available_slots': center.count - operators.count(),
        'capacity_percentage': int((operators.count() / center.count) * 100) if center.count > 0 else 0
    }
    
    return render(request, 'center_detail.html', context)

def operators(request):

    if not request.user.is_authenticated:
        return render(request, 'login.html')

    operators = Operator.objects.all()
    centers = Center.objects.all()

    context = {
        'operators': operators,
        'centers': centers
    }
    
    return render(request, 'operators.html', context)

@csrf_exempt
def create_operator(request):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'Authentication required'}, status=401)
        
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name')
            phone = data.get('phone')
            center_id = data.get('center')
            
            # Validate input
            if not name:
                return JsonResponse({'success': False, 'message': 'Name is required'}, status=400)
            
            # Get center if provided
            center = None
            if center_id:
                try:
                    center = Center.objects.get(pk=center_id)
                except Center.DoesNotExist:
                    return JsonResponse({'success': False, 'message': 'Selected center does not exist'}, status=404)
            
            # Create new operator
            operator = Operator.objects.create(
                name=name,
                phone=phone if phone else None,
                center=center,
                created_by=request.user
            )
            
            # Return success response with operator data
            return JsonResponse({
                'success': True,
                'message': 'Operator created successfully',
                'operator': {
                    'id': operator.id,
                    'name': operator.name,
                    'phone': operator.phone or '',
                    'center': {
                        'id': center.id,
                        'name': center.name
                    } if center else None,
                    'created_by': request.user.get_full_name() or request.user.username
                }
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)
    
    return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=405)

@csrf_exempt
def update_operator(request, operator_id):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'Authentication required'}, status=401)
        
    if request.method == 'PUT':
        try:
            # Get the operator
            operator = get_object_or_404(Operator, id=operator_id)
            
            # Parse the data
            data = json.loads(request.body)
            name = data.get('name')
            phone = data.get('phone')
            center_id = data.get('center')
            
            # Validate input
            if not name:
                return JsonResponse({'success': False, 'message': 'Name is required'}, status=400)
            
            # Update operator information
            operator.name = name
            operator.phone = phone if phone else None
            
            # Update center if provided
            if center_id:
                try:
                    center = Center.objects.get(pk=center_id)
                    operator.center = center
                except Center.DoesNotExist:
                    return JsonResponse({'success': False, 'message': 'Selected center does not exist'}, status=404)
            else:
                operator.center = None
            
            # Save the changes
            operator.save()
            
            # Return success response
            return JsonResponse({
                'success': True,
                'message': 'Operator updated successfully',
                'operator': {
                    'id': operator.id,
                    'name': operator.name,
                    'phone': operator.phone or '',
                    'center': {
                        'id': operator.center.id,
                        'name': operator.center.name
                    } if operator.center else None,
                    'created_by': operator.created_by.get_full_name() or operator.created_by.username if operator.created_by else 'Not assigned'
                }
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)
    
    return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=405)

@csrf_exempt
def delete_operator(request, operator_id):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'Authentication required'}, status=401)
        
    if request.method == 'DELETE':
        try:
            # Get the operator
            operator = get_object_or_404(Operator, id=operator_id)
            
            # Delete the operator
            operator.delete()
            
            # Return success response
            return JsonResponse({
                'success': True,
                'message': 'Operator deleted successfully'
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)
    
    return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=405)

@csrf_exempt
def add_operators_to_center(request, center_id):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'Authentication required'}, status=401)
        
    if request.method == 'POST':
        try:
            # Get the center
            center = get_object_or_404(Center, id=center_id)
            
            # Parse the data
            data = json.loads(request.body)
            operator_ids = data.get('operators', [])
            
            # Validate input
            if not operator_ids:
                return JsonResponse({'success': False, 'message': 'No operators selected'}, status=400)
            
            # Check if adding these operators would exceed the center's capacity
            current_operator_count = center.operators.count()
            if current_operator_count + len(operator_ids) > center.count:
                return JsonResponse({
                    'success': False, 
                    'message': f'Adding these operators would exceed the center\'s capacity of {center.count}'
                }, status=400)
            
            # Get all operators from the IDs
            operators = Operator.objects.filter(id__in=operator_ids)
            if len(operators) != len(operator_ids):
                return JsonResponse({'success': False, 'message': 'Some selected operators do not exist'}, status=404)
            
            # Check if any operator already has a center
            already_assigned = []
            for operator in operators:
                if operator.center is not None:
                    already_assigned.append(operator.name)
            
            if already_assigned:
                operator_names = ', '.join(already_assigned)
                return JsonResponse({
                    'success': False, 
                    'message': f'Some operators are already assigned to a center: {operator_names}'
                }, status=400)
            
            # Update all operators to belong to this center
            for operator in operators:
                operator.center = center
                operator.save()
            
            # Return success response
            return JsonResponse({
                'success': True,
                'message': f'{len(operators)} operators added to {center.name} successfully'
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)
    
    return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=405)

@csrf_exempt
def remove_operator_from_center(request, center_id, operator_id):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'Authentication required'}, status=401)
        
    if request.method == 'POST':
        try:
            # Get the center and operator
            center = get_object_or_404(Center, id=center_id)
            operator = get_object_or_404(Operator, id=operator_id)
            
            # Check if operator belongs to this center
            if operator.center != center:
                return JsonResponse({
                    'success': False, 
                    'message': 'This operator is not assigned to this center'
                }, status=400)
            
            # Remove operator from center
            operator.center = None
            operator.save()
            
            # Return success response
            return JsonResponse({
                'success': True,
                'message': f'Operator {operator.name} removed from {center.name} successfully'
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)
    
    return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=405)