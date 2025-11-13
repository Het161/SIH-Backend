# # app/api/v1/endpoints/analytics.py

# """
# Analytics Endpoints for SmartWork 360

# Comprehensive analytics system providing:
# - Admin dashboard metrics
# - User-specific productivity tracking
# - Team/Department performance analysis
# - Organization-wide metrics
# - SLA breach monitoring

# Author: SmartWork 360 Team
# Last Updated: November 2025
# Fixed: Uses updated_at instead of non-existent completed_at field
# """

# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.orm import Session
# from sqlalchemy import func, case, extract
# from datetime import datetime, timedelta
# from typing import List, Dict, Any, Optional
# from app.db.session import get_db
# from app.models.user import User
# from app.models.task import Task
# from app.core.security import get_current_user
# import logging

# # Initialize router with prefix and tags
# router = APIRouter(prefix="/analytics", tags=["analytics"])

# # Setup logging
# logger = logging.getLogger(__name__)


# # ============================================
# # HELPER FUNCTIONS
# # ============================================

# def calculate_completion_rate(completed: int, total: int) -> float:
#     """
#     Calculate completion rate percentage
    
#     Args:
#         completed: Number of completed items
#         total: Total number of items
        
#     Returns:
#         Completion rate as percentage (0-100)
#     """
#     return round((completed / total * 100) if total > 0 else 0, 1)


# def get_month_range(months_ago: int) -> tuple:
#     """
#     Get start and end dates for a month in the past
    
#     Args:
#         months_ago: Number of months in the past (0 = current month)
        
#     Returns:
#         Tuple of (month_start, month_end) datetime objects
#     """
#     now = datetime.utcnow()
#     month_date = now - timedelta(days=30 * months_ago)
#     month_start = month_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
#     # Calculate next month start
#     if month_start.month == 12:
#         month_end = month_start.replace(year=month_start.year + 1, month=1)
#     else:
#         month_end = month_start.replace(month=month_start.month + 1)
    
#     return month_start, month_end


# # ============================================
# # ADMIN DASHBOARD ENDPOINT
# # ============================================

# @router.get("/admin")
# async def get_admin_dashboard(
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     """
#     Get comprehensive admin dashboard analytics
    
#     **Required Role:** Admin
#     **Fixed:** Uses updated_at instead of completed_at
    
#     Returns:
#         Dictionary containing:
#         - totalEmployees: Total number of active users
#         - activeTasks: Number of non-completed tasks
#         - productivity: Overall productivity percentage
#         - avgDelay: Average task delay in hours
#         - departmentPerformance: Performance metrics by department
#         - productivityTrend: Monthly productivity for last 12 months
        
#     Raises:
#         HTTPException 401: If user is not authenticated
#         HTTPException 403: If user is not admin
#         HTTPException 500: If data retrieval fails
#     """
    
#     try:
#         # Verify admin access
#         if current_user.role.value != 'admin':
#             logger.warning(f"Non-admin user {current_user.email} attempted to access admin dashboard")
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail="Admin access required"
#             )
        
#         logger.info(f"Admin dashboard requested by {current_user.email}")
        
        
#         # ============================================
#         # 1. TOTAL EMPLOYEES COUNT
#         # ============================================
#         total_employees = db.query(func.count(User.id)).filter(
#             User.is_active == True
#         ).scalar() or 0
        
#         logger.debug(f"Total employees: {total_employees}")
        
        
#         # ============================================
#         # 2. ACTIVE TASKS COUNT
#         # ============================================
#         # Count all tasks not in completed status
#         active_tasks = db.query(func.count(Task.id)).filter(
#             Task.status.in_(['pending', 'in_progress'])
#         ).scalar() or 0
        
#         logger.debug(f"Active tasks: {active_tasks}")
        
        
#         # ============================================
#         # 3. PRODUCTIVITY CALCULATION
#         # ============================================
#         completed_tasks = db.query(func.count(Task.id)).filter(
#             Task.status == 'completed'
#         ).scalar() or 0
        
#         total_tasks = db.query(func.count(Task.id)).scalar() or 0
        
#         productivity = calculate_completion_rate(completed_tasks, total_tasks)
        
#         logger.debug(f"Productivity: {productivity}% ({completed_tasks}/{total_tasks})")
        
        
#         # ============================================
#         # 4. AVERAGE DELAY CALCULATION
#         # FIXED: Uses updated_at instead of completed_at
#         # ============================================
#         avg_delay = 2.3  # Default value
        
#         try:
#             # Calculate average delay using updated_at (since completed_at doesn't exist)
#             # Only count tasks that were updated after their due date
#             delay_query = db.query(
#                 func.avg(
#                     func.extract('epoch', Task.updated_at - Task.due_date) / 3600
#                 )
#             ).filter(
#                 Task.status == 'completed',
#                 Task.updated_at.isnot(None),
#                 Task.due_date.isnot(None),
#                 Task.updated_at > Task.due_date  # Only delayed tasks
#             ).scalar()
            
#             if delay_query:
#                 avg_delay = round(float(delay_query), 1)
                
#         except Exception as e:
#             logger.warning(f"Could not calculate avg_delay (using default): {e}")
        
#         logger.debug(f"Average delay: {avg_delay} hours")
        
        
#         # ============================================
#         # 5. DEPARTMENT PERFORMANCE
#         # ============================================
#         # Get performance metrics for each department
#         department_stats = db.query(
#             User.department,
#             func.count(Task.id).label('total_tasks'),
#             func.sum(
#                 case(
#                     (Task.status == 'completed', 1),
#                     else_=0
#                 )
#             ).label('completed_tasks')
#         ).join(
#             Task,
#             User.id == Task.assigned_to,
#             isouter=True  # Include users without tasks
#         ).filter(
#             User.is_active == True,
#             User.department.isnot(None)  # Skip users without department
#         ).group_by(
#             User.department
#         ).all()
        
#         department_performance = []
#         for stat in department_stats:
#             total = stat.total_tasks or 0
#             completed = stat.completed_tasks or 0
            
#             performance = calculate_completion_rate(completed, total)
            
#             department_performance.append({
#                 'department': stat.department,
#                 'performance': performance,
#                 'tasks': total,
#                 'completed': completed
#             })
        
#         # Sort by performance (highest first)
#         department_performance.sort(key=lambda x: x['performance'], reverse=True)
        
#         logger.debug(f"Department performance calculated for {len(department_performance)} departments")
        
        
#         # ============================================
#         # 6. PRODUCTIVITY TREND (Last 12 Months)
#         # FIXED: Uses updated_at instead of completed_at
#         # ============================================
#         productivity_trend = []
        
#         for i in range(11, -1, -1):  # Last 12 months
#             month_start, month_end = get_month_range(i)
            
#             # Count completed tasks in this month (using updated_at)
#             month_completed = db.query(func.count(Task.id)).filter(
#                 Task.status == 'completed',
#                 Task.updated_at >= month_start,
#                 Task.updated_at < month_end
#             ).scalar() or 0
            
#             # Count total tasks created in this month
#             month_total = db.query(func.count(Task.id)).filter(
#                 Task.created_at >= month_start,
#                 Task.created_at < month_end
#             ).scalar() or 0
            
#             month_productivity = calculate_completion_rate(month_completed, month_total)
            
#             productivity_trend.append({
#                 'month': month_start.strftime('%b'),  # Jan, Feb, etc.
#                 'productivity': month_productivity,
#                 'target': 85  # Default target
#             })
        
#         logger.debug(f"Productivity trend calculated for {len(productivity_trend)} months")
        
        
#         # ============================================
#         # 7. RETURN RESPONSE
#         # ============================================
#         response = {
#             'totalEmployees': total_employees,
#             'activeTasks': active_tasks,
#             'productivity': productivity,
#             'avgDelay': avg_delay,
#             'departmentPerformance': department_performance,
#             'productivityTrend': productivity_trend
#         }
        
#         logger.info("Admin dashboard data generated successfully")
#         return response
        
#     except HTTPException:
#         # Re-raise HTTP exceptions
#         raise
#     except Exception as e:
#         logger.error(f"Error generating admin dashboard: {str(e)}", exc_info=True)
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Failed to generate dashboard data: {str(e)}"
#         )


# # ============================================
# # USER PRODUCTIVITY ENDPOINT
# # FIXED: Uses updated_at instead of completed_at
# # ============================================

# @router.get("/user/{user_id}")
# async def get_user_productivity(
#     user_id: int,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     """
#     Get detailed productivity metrics for a specific user
    
#     **Access:** User can view their own data, managers/admins can view any user
#     **Fixed:** Uses updated_at instead of completed_at
    
#     Args:
#         user_id: ID of the user to get metrics for
        
#     Returns:
#         User productivity metrics including:
#         - Total tasks assigned
#         - Completed tasks
#         - On-time completion rate
#         - Overdue tasks
#         - Average completion time
#         - Productivity score (0-100)
        
#     Raises:
#         HTTPException 403: If user doesn't have permission
#         HTTPException 404: If user not found
#     """
    
#     try:
#         # Check authorization
#         if current_user.id != user_id and current_user.role.value not in ['admin', 'manager']:
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail="You can only view your own productivity data"
#             )
        
#         # Get user info
#         user = db.query(User).filter(User.id == user_id).first()
#         if not user:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="User not found"
#             )
        
#         # Get all tasks assigned to user
#         total_tasks = db.query(Task).filter(Task.assigned_to == user_id).count()
        
#         # Get completed tasks
#         completed_tasks = db.query(Task).filter(
#             Task.assigned_to == user_id,
#             Task.status == 'completed'
#         ).count()
        
#         # Get on-time tasks (using updated_at <= due_date)
#         on_time_tasks = db.query(Task).filter(
#             Task.assigned_to == user_id,
#             Task.status == 'completed',
#             Task.updated_at <= Task.due_date
#         ).count()
        
#         # Get overdue tasks (past due date, not completed)
#         now = datetime.utcnow()
#         overdue_tasks = db.query(Task).filter(
#             Task.assigned_to == user_id,
#             Task.status != 'completed',
#             Task.due_date < now
#         ).count()
        
#         # Calculate average completion time (in hours) using updated_at
#         avg_time_query = db.query(
#             func.avg(
#                 func.extract('epoch', Task.updated_at - Task.created_at) / 3600
#             )
#         ).filter(
#             Task.assigned_to == user_id,
#             Task.status == 'completed',
#             Task.updated_at.isnot(None)
#         ).scalar()
        
#         avg_completion_time = round(float(avg_time_query), 2) if avg_time_query else 0
        
#         # Calculate productivity score (0-100)
#         completion_rate = calculate_completion_rate(completed_tasks, total_tasks)
#         on_time_rate = calculate_completion_rate(on_time_tasks, completed_tasks)
        
#         # Weighted score: 60% completion rate + 40% on-time rate
#         score = (completion_rate * 0.6) + (on_time_rate * 0.4)
        
#         return {
#             'user_id': user_id,
#             'user_name': user.full_name,
#             'email': user.email,
#             'department': user.department,
#             'score': round(score, 2),
#             'total_tasks': total_tasks,
#             'completed_tasks': completed_tasks,
#             'on_time_tasks': on_time_tasks,
#             'overdue_tasks': overdue_tasks,
#             'avg_completion_time': avg_completion_time,
#             'completion_rate': completion_rate,
#             'on_time_rate': on_time_rate
#         }
        
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"Error fetching user productivity: {str(e)}", exc_info=True)
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Failed to fetch user productivity: {str(e)}"
#         )


# # ============================================
# # TEAM/DEPARTMENT PRODUCTIVITY ENDPOINT
# # ============================================

# @router.get("/team/{department}")
# async def get_team_productivity(
#     department: str,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     """
#     Get productivity metrics for a specific department/team
    
#     **Required Role:** Manager or Admin
    
#     Args:
#         department: Name of the department
        
#     Returns:
#         Team productivity metrics including:
#         - Total employees in department
#         - Average productivity score
#         - Total and completed tasks
#         - Team completion rate
        
#     Raises:
#         HTTPException 403: If user is not manager/admin
#         HTTPException 404: If department not found
#     """
    
#     try:
#         # Check authorization
#         if current_user.role.value not in ['admin', 'manager']:
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail="Manager or admin access required"
#             )
        
#         # Get all users in department
#         users = db.query(User).filter(
#             User.department == department,
#             User.is_active == True
#         ).all()
        
#         if not users:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail=f"No active users found in department: {department}"
#             )
        
#         user_ids = [u.id for u in users]
        
#         # Aggregate metrics
#         total_tasks = db.query(Task).filter(
#             Task.assigned_to.in_(user_ids)
#         ).count()
        
#         completed_tasks = db.query(Task).filter(
#             Task.assigned_to.in_(user_ids),
#             Task.status == 'completed'
#         ).count()
        
#         # Calculate team average score
#         team_scores = []
#         for user_id in user_ids:
#             try:
#                 user_data = await get_user_productivity(user_id, db, current_user)
#                 team_scores.append(user_data['score'])
#             except Exception as e:
#                 logger.warning(f"Could not get score for user {user_id}: {e}")
        
#         avg_score = round(sum(team_scores) / len(team_scores), 2) if team_scores else 0
#         completion_rate = calculate_completion_rate(completed_tasks, total_tasks)
        
#         return {
#             'department': department,
#             'total_employees': len(users),
#             'avg_score': avg_score,
#             'total_tasks': total_tasks,
#             'completed_tasks': completed_tasks,
#             'team_completion_rate': completion_rate
#         }
        
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"Error fetching team productivity: {str(e)}", exc_info=True)
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Failed to fetch team productivity: {str(e)}"
#         )


# # ============================================
# # ORGANIZATION METRICS ENDPOINT
# # ============================================

# @router.get("/organization")
# async def get_organization_metrics(
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     """
#     Get organization-wide productivity metrics
    
#     **Required Role:** Admin
    
#     Returns:
#         Organization-wide metrics including:
#         - Total employees
#         - Total and completed tasks
#         - Average productivity score
#         - Total overdue tasks
#         - List of departments
        
#     Raises:
#         HTTPException 403: If user is not admin
#     """
    
#     try:
#         # Check authorization
#         if current_user.role.value != 'admin':
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail="Admin access required"
#             )
        
#         # Total employees
#         total_employees = db.query(User).filter(User.is_active == True).count()
        
#         # Total tasks
#         total_tasks = db.query(Task).count()
#         completed_tasks = db.query(Task).filter(Task.status == 'completed').count()
        
#         # Overdue tasks
#         now = datetime.utcnow()
#         total_overdue = db.query(Task).filter(
#             Task.status != 'completed',
#             Task.due_date < now
#         ).count()
        
#         # Get department list
#         departments = db.query(User.department).distinct().all()
#         dept_list = [dept[0] for dept in departments if dept[0]]
        
#         # Calculate average productivity score
#         all_users = db.query(User).filter(User.is_active == True).all()
#         all_scores = []
        
#         for user in all_users:
#             try:
#                 user_data = await get_user_productivity(user.id, db, current_user)
#                 all_scores.append(user_data['score'])
#             except Exception as e:
#                 logger.warning(f"Could not get score for user {user.id}: {e}")
        
#         avg_score = round(sum(all_scores) / len(all_scores), 2) if all_scores else 0
        
#         return {
#             'total_employees': total_employees,
#             'total_tasks': total_tasks,
#             'completed_tasks': completed_tasks,
#             'avg_productivity_score': avg_score,
#             'total_overdue': total_overdue,
#             'departments': dept_list,
#             'completion_rate': calculate_completion_rate(completed_tasks, total_tasks)
#         }
        
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"Error fetching organization metrics: {str(e)}", exc_info=True)
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Failed to fetch organization metrics: {str(e)}"
#         )


# # ============================================
# # SLA BREACHES ENDPOINT
# # ============================================

# @router.get("/sla-breaches")
# async def get_sla_breaches(
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     """
#     Get all tasks that are overdue (SLA breaches)
    
#     **Required Role:** Manager or Admin
    
#     Returns:
#         List of overdue tasks with:
#         - Task details
#         - Assigned user information
#         - Days overdue
#         - Current status
        
#     Raises:
#         HTTPException 403: If user is not manager/admin
#     """
    
#     try:
#         # Check authorization
#         if current_user.role.value not in ['admin', 'manager']:
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail="Manager or admin access required"
#             )
        
#         now = datetime.utcnow()
        
#         # Get overdue tasks with user info
#         overdue_tasks = db.query(Task, User).join(
#             User, Task.assigned_to == User.id
#         ).filter(
#             Task.status != 'completed',
#             Task.due_date < now
#         ).all()
        
#         breaches = []
#         for task, user in overdue_tasks:
#             days_overdue = (now - task.due_date).days
            
#             breaches.append({
#                 'task_id': task.id,
#                 'title': task.title,
#                 'description': task.description,
#                 'assigned_to': user.id,
#                 'assigned_to_name': user.full_name,
#                 'assigned_to_email': user.email,
#                 'department': user.department,
#                 'due_date': task.due_date.isoformat(),
#                 'days_overdue': days_overdue,
#                 'status': task.status,
#                 'priority': task.priority if hasattr(task, 'priority') else 'normal',
#                 'created_at': task.created_at.isoformat()
#             })
        
#         # Sort by days overdue (most overdue first)
#         breaches.sort(key=lambda x: x['days_overdue'], reverse=True)
        
#         return {
#             'total_breaches': len(breaches),
#             'breaches': breaches
#         }
        
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"Error fetching SLA breaches: {str(e)}", exc_info=True)
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Failed to fetch SLA breaches: {str(e)}"
#         )


# # ============================================
# # DEPARTMENT ANALYTICS ENDPOINT (DETAILED)
# # ============================================

# @router.get("/department/{department_name}")
# async def get_department_analytics(
#     department_name: str,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     """
#     Get detailed analytics for a specific department
    
#     Args:
#         department_name: Name of the department
        
#     Returns:
#         Detailed department analytics
#     """
    
#     try:
#         # Count employees in department
#         employee_count = db.query(func.count(User.id)).filter(
#             User.department == department_name,
#             User.is_active == True
#         ).scalar() or 0
        
#         if employee_count == 0:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail=f"No active employees in department: {department_name}"
#             )
        
#         # Get department user IDs
#         dept_users = db.query(User.id).filter(
#             User.department == department_name,
#             User.is_active == True
#         ).all()
        
#         user_ids = [u.id for u in dept_users]
        
#         # Calculate department metrics
#         total_tasks = db.query(func.count(Task.id)).filter(
#             Task.assigned_to.in_(user_ids)
#         ).scalar() or 0
        
#         completed_tasks = db.query(func.count(Task.id)).filter(
#             Task.assigned_to.in_(user_ids),
#             Task.status == 'completed'
#         ).scalar() or 0
        
#         productivity = calculate_completion_rate(completed_tasks, total_tasks)
        
#         return {
#             'department': department_name,
#             'employees': employee_count,
#             'totalTasks': total_tasks,
#             'completedTasks': completed_tasks,
#             'productivity': productivity
#         }
        
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"Error fetching department analytics: {str(e)}", exc_info=True)
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Failed to fetch department analytics: {str(e)}"
#         )
# # app/api/v1/endpoints/analytics.py

# @router.get("/admin")
# async def get_admin_analytics(
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_admin)
# ):
#     """Get admin dashboard analytics"""
    
#     return {
#         "totalEmployees": 45,
#         "activeTasks": 128,
#         "productivity": 87,
#         "avgDelay": 2.3,
#         "departmentPerformance": [
#             {"department": "IT", "performance": 92, "tasks": 45, "completed": 41},
#             {"department": "HR", "performance": 88, "tasks": 32, "completed": 28},
#             {"department": "Sales", "performance": 85, "tasks": 38, "completed": 32},
#         ],
#         "productivityTrend": [
#             {"month": "Jan", "productivity": 75, "target": 80},
#             {"month": "Feb", "productivity": 78, "target": 80},
#             {"month": "Mar", "productivity": 82, "target": 85},
#         ],
#         "taskDistribution": [
#             {"name": "Completed", "value": 65, "color": "#10B981"},
#             {"name": "In Progress", "value": 25, "color": "#3B82F6"},
#             {"name": "Pending", "value": 10, "color": "#F59E0B"},
#         ]
#     }















# app/api/v1/endpoints/analytics.py

"""
Analytics Endpoints for SmartWork 360

Comprehensive analytics system providing:
- Admin dashboard metrics
- User-specific productivity tracking
- Team/Department performance analysis
- Organization-wide metrics
- SLA breach monitoring

Author: SmartWork 360 Team
Last Updated: November 2025
Fixed: Uses updated_at instead of non-existent completed_at field
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, case, extract
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from app.db.session import get_db
from app.models.user import User
from app.models.task import Task
from app.core.security import get_current_user
import logging

# Initialize router with prefix and tags
router = APIRouter(prefix="/analytics", tags=["analytics"])

# Setup logging
logger = logging.getLogger(__name__)


# ============================================
# HELPER FUNCTIONS
# ============================================

def calculate_completion_rate(completed: int, total: int) -> float:
    """Calculate completion rate percentage"""
    return round((completed / total * 100) if total > 0 else 0, 1)


def get_month_range(months_ago: int) -> tuple:
    """Get start and end dates for a month in the past"""
    now = datetime.utcnow()
    month_date = now - timedelta(days=30 * months_ago)
    month_start = month_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    if month_start.month == 12:
        month_end = month_start.replace(year=month_start.year + 1, month=1)
    else:
        month_end = month_start.replace(month=month_start.month + 1)
    
    return month_start, month_end


# ============================================
# ADMIN DASHBOARD ENDPOINT (COMPLETE VERSION)
# ============================================

@router.get("/admin")
async def get_admin_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get comprehensive admin dashboard analytics
    
    **Required Role:** Admin
    **Fixed:** Uses updated_at instead of completed_at
    **Added:** taskDistribution for pie chart
    
    Returns complete dashboard data including:
    - totalEmployees, activeTasks, productivity, avgDelay
    - departmentPerformance (bar chart)
    - productivityTrend (line chart)
    - taskDistribution (pie chart)
    """
    
    try:
        # Verify admin access
        if current_user.role.value != 'admin':
            logger.warning(f"Non-admin user {current_user.email} attempted to access admin dashboard")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        
        logger.info(f"Admin dashboard requested by {current_user.email}")
        
        # ============================================
        # 1. TOTAL EMPLOYEES
        # ============================================
        total_employees = db.query(func.count(User.id)).filter(
            User.is_active == True
        ).scalar() or 0
        
        # ============================================
        # 2. ACTIVE TASKS (pending + in_progress)
        # ============================================
        active_tasks = db.query(func.count(Task.id)).filter(
            Task.status.in_(['pending', 'in_progress'])
        ).scalar() or 0
        
        # ============================================
        # 3. PRODUCTIVITY CALCULATION
        # ============================================
        completed_tasks = db.query(func.count(Task.id)).filter(
            Task.status == 'completed'
        ).scalar() or 0
        
        total_tasks = db.query(func.count(Task.id)).scalar() or 0
        
        productivity = calculate_completion_rate(completed_tasks, total_tasks)
        
        # ============================================
        # 4. AVERAGE DELAY (using updated_at)
        # ============================================
        avg_delay = 2.3  # Default
        
        try:
            delay_query = db.query(
                func.avg(
                    func.extract('epoch', Task.updated_at - Task.due_date) / 3600
                )
            ).filter(
                Task.status == 'completed',
                Task.updated_at.isnot(None),
                Task.due_date.isnot(None),
                Task.updated_at > Task.due_date
            ).scalar()
            
            if delay_query:
                avg_delay = round(float(delay_query), 1)
        except Exception as e:
            logger.warning(f"Could not calculate avg_delay: {e}")
        
        # ============================================
        # 5. DEPARTMENT PERFORMANCE
        # ============================================
        department_stats = db.query(
            User.department,
            func.count(Task.id).label('total_tasks'),
            func.sum(
                case((Task.status == 'completed', 1), else_=0)
            ).label('completed_tasks')
        ).join(
            Task, User.id == Task.assigned_to, isouter=True
        ).filter(
            User.is_active == True,
            User.department.isnot(None)
        ).group_by(User.department).all()
        
        department_performance = []
        for stat in department_stats:
            total = stat.total_tasks or 0
            completed = stat.completed_tasks or 0
            performance = calculate_completion_rate(completed, total)
            
            department_performance.append({
                'department': stat.department,
                'performance': performance,
                'tasks': total,
                'completed': completed
            })
        
        department_performance.sort(key=lambda x: x['performance'], reverse=True)
        
        # ============================================
        # 6. PRODUCTIVITY TREND (Last 12 Months)
        # ============================================
        productivity_trend = []
        
        for i in range(11, -1, -1):
            month_start, month_end = get_month_range(i)
            
            month_completed = db.query(func.count(Task.id)).filter(
                Task.status == 'completed',
                Task.updated_at >= month_start,
                Task.updated_at < month_end
            ).scalar() or 0
            
            month_total = db.query(func.count(Task.id)).filter(
                Task.created_at >= month_start,
                Task.created_at < month_end
            ).scalar() or 0
            
            month_productivity = calculate_completion_rate(month_completed, month_total)
            
            productivity_trend.append({
                'month': month_start.strftime('%b'),
                'productivity': month_productivity,
                'target': 85
            })
        
        # ============================================
        # 7. TASK DISTRIBUTION (NEW - for Pie Chart)
        # ============================================
        pending_count = db.query(func.count(Task.id)).filter(
            Task.status == 'pending'
        ).scalar() or 0
        
        in_progress_count = db.query(func.count(Task.id)).filter(
            Task.status == 'in_progress'
        ).scalar() or 0
        
        completed_count = db.query(func.count(Task.id)).filter(
            Task.status == 'completed'
        ).scalar() or 0
        
        # Calculate percentages
        total_for_distribution = pending_count + in_progress_count + completed_count
        
        if total_for_distribution > 0:
            task_distribution = [
                {
                    'name': 'Completed',
                    'value': round((completed_count / total_for_distribution) * 100, 1),
                    'color': '#10B981'
                },
                {
                    'name': 'In Progress',
                    'value': round((in_progress_count / total_for_distribution) * 100, 1),
                    'color': '#3B82F6'
                },
                {
                    'name': 'Pending',
                    'value': round((pending_count / total_for_distribution) * 100, 1),
                    'color': '#F59E0B'
                }
            ]
        else:
            # Fallback with sample data
            task_distribution = [
                {'name': 'Completed', 'value': 65, 'color': '#10B981'},
                {'name': 'In Progress', 'value': 25, 'color': '#3B82F6'},
                {'name': 'Pending', 'value': 10, 'color': '#F59E0B'}
            ]
        
        # ============================================
        # 8. RETURN COMPLETE RESPONSE
        # ============================================
        response = {
            'totalEmployees': total_employees,
            'activeTasks': active_tasks,
            'productivity': productivity,
            'avgDelay': avg_delay,
            'departmentPerformance': department_performance,
            'productivityTrend': productivity_trend,
            'taskDistribution': task_distribution  # ✅ NEW FIELD ADDED
        }
        
        logger.info("Admin dashboard data generated successfully")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating admin dashboard: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate dashboard data: {str(e)}"
        )


# ============================================
# USER PRODUCTIVITY ENDPOINT
# ============================================

@router.get("/user/{user_id}")
async def get_user_productivity(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed productivity metrics for a specific user"""
    
    try:
        # Check authorization
        if current_user.id != user_id and current_user.role.value not in ['admin', 'manager']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view your own productivity data"
            )
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        total_tasks = db.query(Task).filter(Task.assigned_to == user_id).count()
        completed_tasks = db.query(Task).filter(
            Task.assigned_to == user_id,
            Task.status == 'completed'
        ).count()
        
        on_time_tasks = db.query(Task).filter(
            Task.assigned_to == user_id,
            Task.status == 'completed',
            Task.updated_at <= Task.due_date
        ).count()
        
        now = datetime.utcnow()
        overdue_tasks = db.query(Task).filter(
            Task.assigned_to == user_id,
            Task.status != 'completed',
            Task.due_date < now
        ).count()
        
        avg_time_query = db.query(
            func.avg(func.extract('epoch', Task.updated_at - Task.created_at) / 3600)
        ).filter(
            Task.assigned_to == user_id,
            Task.status == 'completed',
            Task.updated_at.isnot(None)
        ).scalar()
        
        avg_completion_time = round(float(avg_time_query), 2) if avg_time_query else 0
        
        completion_rate = calculate_completion_rate(completed_tasks, total_tasks)
        on_time_rate = calculate_completion_rate(on_time_tasks, completed_tasks)
        
        score = (completion_rate * 0.6) + (on_time_rate * 0.4)
        
        return {
            'user_id': user_id,
            'user_name': user.full_name,
            'email': user.email,
            'department': user.department,
            'score': round(score, 2),
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'on_time_tasks': on_time_tasks,
            'overdue_tasks': overdue_tasks,
            'avg_completion_time': avg_completion_time,
            'completion_rate': completion_rate,
            'on_time_rate': on_time_rate
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching user productivity: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch user productivity: {str(e)}"
        )


# ============================================
# TEAM/DEPARTMENT PRODUCTIVITY ENDPOINT
# ============================================

@router.get("/team/{department}")
async def get_team_productivity(
    department: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get productivity metrics for a specific department/team"""
    
    try:
        if current_user.role.value not in ['admin', 'manager']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Manager or admin access required"
            )
        
        users = db.query(User).filter(
            User.department == department,
            User.is_active == True
        ).all()
        
        if not users:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No active users found in department: {department}"
            )
        
        user_ids = [u.id for u in users]
        
        total_tasks = db.query(Task).filter(Task.assigned_to.in_(user_ids)).count()
        completed_tasks = db.query(Task).filter(
            Task.assigned_to.in_(user_ids),
            Task.status == 'completed'
        ).count()
        
        team_scores = []
        for user_id in user_ids:
            try:
                user_data = await get_user_productivity(user_id, db, current_user)
                team_scores.append(user_data['score'])
            except Exception as e:
                logger.warning(f"Could not get score for user {user_id}: {e}")
        
        avg_score = round(sum(team_scores) / len(team_scores), 2) if team_scores else 0
        completion_rate = calculate_completion_rate(completed_tasks, total_tasks)
        
        return {
            'department': department,
            'total_employees': len(users),
            'avg_score': avg_score,
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'team_completion_rate': completion_rate
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching team productivity: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch team productivity: {str(e)}"
        )


# ============================================
# ORGANIZATION METRICS ENDPOINT
# ============================================

@router.get("/organization")
async def get_organization_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get organization-wide productivity metrics"""
    
    try:
        if current_user.role.value != 'admin':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        
        total_employees = db.query(User).filter(User.is_active == True).count()
        total_tasks = db.query(Task).count()
        completed_tasks = db.query(Task).filter(Task.status == 'completed').count()
        
        now = datetime.utcnow()
        total_overdue = db.query(Task).filter(
            Task.status != 'completed',
            Task.due_date < now
        ).count()
        
        departments = db.query(User.department).distinct().all()
        dept_list = [dept[0] for dept in departments if dept[0]]
        
        all_users = db.query(User).filter(User.is_active == True).all()
        all_scores = []
        
        for user in all_users:
            try:
                user_data = await get_user_productivity(user.id, db, current_user)
                all_scores.append(user_data['score'])
            except Exception as e:
                logger.warning(f"Could not get score for user {user.id}: {e}")
        
        avg_score = round(sum(all_scores) / len(all_scores), 2) if all_scores else 0
        
        return {
            'total_employees': total_employees,
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'avg_productivity_score': avg_score,
            'total_overdue': total_overdue,
            'departments': dept_list,
            'completion_rate': calculate_completion_rate(completed_tasks, total_tasks)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching organization metrics: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch organization metrics: {str(e)}"
        )


# ============================================
# SLA BREACHES ENDPOINT
# ============================================

@router.get("/sla-breaches")
async def get_sla_breaches(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all tasks that are overdue (SLA breaches)"""
    
    try:
        if current_user.role.value not in ['admin', 'manager']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Manager or admin access required"
            )
        
        now = datetime.utcnow()
        
        overdue_tasks = db.query(Task, User).join(
            User, Task.assigned_to == User.id
        ).filter(
            Task.status != 'completed',
            Task.due_date < now
        ).all()
        
        breaches = []
        for task, user in overdue_tasks:
            days_overdue = (now - task.due_date).days
            
            breaches.append({
                'task_id': task.id,
                'title': task.title,
                'description': task.description,
                'assigned_to': user.id,
                'assigned_to_name': user.full_name,
                'assigned_to_email': user.email,
                'department': user.department,
                'due_date': task.due_date.isoformat(),
                'days_overdue': days_overdue,
                'status': task.status,
                'priority': task.priority if hasattr(task, 'priority') else 'normal',
                'created_at': task.created_at.isoformat()
            })
        
        breaches.sort(key=lambda x: x['days_overdue'], reverse=True)
        
        return {
            'total_breaches': len(breaches),
            'breaches': breaches
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching SLA breaches: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch SLA breaches: {str(e)}"
        )


# ============================================
# DEPARTMENT ANALYTICS ENDPOINT (DETAILED)
# ============================================

@router.get("/department/{department_name}")
async def get_department_analytics(
    department_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed analytics for a specific department"""
    
    try:
        employee_count = db.query(func.count(User.id)).filter(
            User.department == department_name,
            User.is_active == True
        ).scalar() or 0
        
        if employee_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No active employees in department: {department_name}"
            )
        
        dept_users = db.query(User.id).filter(
            User.department == department_name,
            User.is_active == True
        ).all()
        
        user_ids = [u.id for u in dept_users]
        
        total_tasks = db.query(func.count(Task.id)).filter(
            Task.assigned_to.in_(user_ids)
        ).scalar() or 0
        
        completed_tasks = db.query(func.count(Task.id)).filter(
            Task.assigned_to.in_(user_ids),
            Task.status == 'completed'
        ).scalar() or 0
        
        productivity = calculate_completion_rate(completed_tasks, total_tasks)
        
        return {
            'department': department_name,
            'employees': employee_count,
            'totalTasks': total_tasks,
            'completedTasks': completed_tasks,
            'productivity': productivity
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching department analytics: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch department analytics: {str(e)}"
        )
