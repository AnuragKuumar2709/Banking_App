"""
Online Banking System - Reporting and Analytics Module
Comprehensive reporting features for banking operations
"""

import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db_connection import db
from account_manager import AccountManager
from transaction_manager import TransactionManager


class BankingAnalytics:
    """Comprehensive analytics and reporting for banking operations"""
    
    @staticmethod
    def get_customer_summary(customer_id: int) -> Dict:
        """Get comprehensive customer summary"""
        try:
            customer = AccountManager.get_customer(customer_id)
            if not customer:
                return {'error': 'Customer not found'}
            
            accounts = AccountManager.get_customer_accounts(customer_id)
            
            # Calculate totals
            total_balance = sum(float(acc['balance']) for acc in accounts)
            active_accounts = [acc for acc in accounts if acc['status'] == 'ACTIVE']
            
            # Get transaction statistics
            total_transactions = 0
            total_deposits = 0
            total_withdrawals = 0
            
            for account in accounts:
                transactions = TransactionManager.get_transaction_history(account['account_id'], 1000)
                total_transactions += len(transactions)
                
                for txn in transactions:
                    if txn['transaction_type'] == 'DEPOSIT':
                        total_deposits += float(txn['amount'])
                    else:
                        total_withdrawals += float(txn['amount'])
            
            return {
                'customer': customer,
                'accounts': {
                    'total': len(accounts),
                    'active': len(active_accounts),
                    'total_balance': total_balance
                },
                'transactions': {
                    'total_count': total_transactions,
                    'total_deposits': total_deposits,
                    'total_withdrawals': total_withdrawals,
                    'net_amount': total_deposits - total_withdrawals
                },
                'account_types': {
                    acc_type: len([acc for acc in accounts if acc['account_type'] == acc_type])
                    for acc_type in ['SAVINGS', 'CHECKING', 'BUSINESS']
                }
            }
        except Exception as e:
            return {'error': str(e)}
    
    @staticmethod
    def get_monthly_transaction_report(account_id: int, months: int = 12) -> Dict:
        """Get monthly transaction report for an account"""
        try:
            account = AccountManager.get_account(account_id)
            if not account:
                return {'error': 'Account not found'}
            
            # Get transactions for the specified period
            end_date = datetime.now()
            start_date = end_date - timedelta(days=months * 30)
            
            query = """
                SELECT 
                    strftime('%Y-%m', transaction_date) as month,
                    transaction_type,
                    COUNT(*) as count,
                    SUM(amount) as total_amount,
                    AVG(amount) as average_amount
                FROM transactions
                WHERE account_id = ? 
                AND transaction_date >= ?
                GROUP BY strftime('%Y-%m', transaction_date), transaction_type
                ORDER BY month DESC
            """
            
            results = db.execute_query(query, (account_id, start_date.strftime('%Y-%m-%d')))
            
            # Organize data by month
            monthly_data = {}
            for row in results:
                month = row['month']
                if month not in monthly_data:
                    monthly_data[month] = {
                        'deposits': {'count': 0, 'total': 0, 'average': 0},
                        'withdrawals': {'count': 0, 'total': 0, 'average': 0}
                    }
                
                txn_type = row['transaction_type'].lower()
                monthly_data[month][txn_type] = {
                    'count': row['count'],
                    'total': float(row['total_amount']),
                    'average': float(row['average_amount'])
                }
            
            return {
                'account': account,
                'period_months': months,
                'monthly_data': monthly_data,
                'summary': {
                    'total_months': len(monthly_data),
                    'total_transactions': sum(
                        sum(data['deposits']['count'] + data['withdrawals']['count'] 
                            for data in monthly_data.values())
                    )
                }
            }
        except Exception as e:
            return {'error': str(e)}
    
    @staticmethod
    def get_account_performance_metrics(account_id: int) -> Dict:
        """Get performance metrics for an account"""
        try:
            account = AccountManager.get_account(account_id)
            if not account:
                return {'error': 'Account not found'}
            
            # Get transaction history
            transactions = TransactionManager.get_transaction_history(account_id, 1000)
            
            if not transactions:
                return {
                    'account': account,
                    'metrics': {
                        'total_transactions': 0,
                        'average_transaction_size': 0,
                        'largest_deposit': 0,
                        'largest_withdrawal': 0,
                        'transaction_frequency': 0,
                        'balance_growth_rate': 0
                    }
                }
            
            # Calculate metrics
            deposits = [txn for txn in transactions if txn['transaction_type'] == 'DEPOSIT']
            withdrawals = [txn for txn in transactions if txn['transaction_type'] == 'WITHDRAWAL']
            
            total_amount = sum(float(txn['amount']) for txn in transactions)
            average_transaction_size = total_amount / len(transactions)
            
            largest_deposit = max((float(txn['amount']) for txn in deposits), default=0)
            largest_withdrawal = max((float(txn['amount']) for txn in withdrawals), default=0)
            
            # Calculate transaction frequency (transactions per month)
            if transactions:
                first_transaction = min(transactions, key=lambda x: x['transaction_date'])
                last_transaction = max(transactions, key=lambda x: x['transaction_date'])
                
                first_date = datetime.strptime(first_transaction['transaction_date'][:10], '%Y-%m-%d')
                last_date = datetime.strptime(last_transaction['transaction_date'][:10], '%Y-%m-%d')
                
                days_diff = (last_date - first_date).days
                months_diff = max(days_diff / 30, 1)  # Avoid division by zero
                transaction_frequency = len(transactions) / months_diff
            else:
                transaction_frequency = 0
            
            # Calculate balance growth rate
            if len(transactions) >= 2:
                first_balance = float(transactions[-1]['balance_after'])  # Oldest transaction
                last_balance = float(transactions[0]['balance_after'])    # Newest transaction
                balance_growth_rate = ((last_balance - first_balance) / first_balance * 100) if first_balance > 0 else 0
            else:
                balance_growth_rate = 0
            
            return {
                'account': account,
                'metrics': {
                    'total_transactions': len(transactions),
                    'deposits_count': len(deposits),
                    'withdrawals_count': len(withdrawals),
                    'total_deposits': sum(float(txn['amount']) for txn in deposits),
                    'total_withdrawals': sum(float(txn['amount']) for txn in withdrawals),
                    'average_transaction_size': average_transaction_size,
                    'largest_deposit': largest_deposit,
                    'largest_withdrawal': largest_withdrawal,
                    'transaction_frequency': transaction_frequency,
                    'balance_growth_rate': balance_growth_rate
                }
            }
        except Exception as e:
            return {'error': str(e)}
    
    @staticmethod
    def get_bank_wide_statistics() -> Dict:
        """Get bank-wide statistics and analytics"""
        try:
            # Customer statistics
            customer_query = "SELECT COUNT(*) as total_customers FROM customers"
            customer_count = db.execute_query(customer_query)[0]['total_customers']
            
            # Account statistics
            account_query = """
                SELECT 
                    COUNT(*) as total_accounts,
                    COUNT(CASE WHEN status = 'ACTIVE' THEN 1 END) as active_accounts,
                    SUM(balance) as total_balance,
                    AVG(balance) as average_balance
                FROM accounts
            """
            account_stats = db.execute_query(account_query)[0]
            
            # Transaction statistics
            transaction_query = """
                SELECT 
                    COUNT(*) as total_transactions,
                    COUNT(CASE WHEN transaction_type = 'DEPOSIT' THEN 1 END) as deposits,
                    COUNT(CASE WHEN transaction_type = 'WITHDRAWAL' THEN 1 END) as withdrawals,
                    SUM(CASE WHEN transaction_type = 'DEPOSIT' THEN amount ELSE 0 END) as total_deposits,
                    SUM(CASE WHEN transaction_type = 'WITHDRAWAL' THEN amount ELSE 0 END) as total_withdrawals
                FROM transactions
            """
            transaction_stats = db.execute_query(transaction_query)[0]
            
            # Transfer statistics
            transfer_query = """
                SELECT 
                    COUNT(*) as total_transfers,
                    COUNT(CASE WHEN status = 'COMPLETED' THEN 1 END) as completed_transfers,
                    SUM(amount) as total_transferred
                FROM transfers
            """
            transfer_stats = db.execute_query(transfer_query)[0]
            
            # Account type distribution
            account_type_query = """
                SELECT 
                    account_type,
                    COUNT(*) as count,
                    SUM(balance) as total_balance
                FROM accounts
                WHERE status = 'ACTIVE'
                GROUP BY account_type
            """
            account_types = db.execute_query(account_type_query)
            
            return {
                'customers': {
                    'total': customer_count
                },
                'accounts': {
                    'total': account_stats['total_accounts'],
                    'active': account_stats['active_accounts'],
                    'total_balance': float(account_stats['total_balance'] or 0),
                    'average_balance': float(account_stats['average_balance'] or 0),
                    'by_type': {row['account_type']: {
                        'count': row['count'],
                        'total_balance': float(row['total_balance'])
                    } for row in account_types}
                },
                'transactions': {
                    'total': transaction_stats['total_transactions'],
                    'deposits': transaction_stats['deposits'],
                    'withdrawals': transaction_stats['withdrawals'],
                    'total_deposits': float(transaction_stats['total_deposits'] or 0),
                    'total_withdrawals': float(transaction_stats['total_withdrawals'] or 0)
                },
                'transfers': {
                    'total': transfer_stats['total_transfers'],
                    'completed': transfer_stats['completed_transfers'],
                    'total_amount': float(transfer_stats['total_transferred'] or 0)
                }
            }
        except Exception as e:
            return {'error': str(e)}
    
    @staticmethod
    def get_transaction_trends(days: int = 30) -> Dict:
        """Get transaction trends over time"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Daily transaction trends
            daily_query = """
                SELECT 
                    DATE(transaction_date) as date,
                    transaction_type,
                    COUNT(*) as count,
                    SUM(amount) as total_amount
                FROM transactions
                WHERE transaction_date >= ?
                GROUP BY DATE(transaction_date), transaction_type
                ORDER BY date DESC
            """
            
            daily_results = db.execute_query(daily_query, (start_date.strftime('%Y-%m-%d'),))
            
            # Organize by date
            daily_trends = {}
            for row in daily_results:
                date = row['date']
                if date not in daily_trends:
                    daily_trends[date] = {
                        'deposits': {'count': 0, 'amount': 0},
                        'withdrawals': {'count': 0, 'amount': 0}
                    }
                
                txn_type = row['transaction_type'].lower()
                daily_trends[date][txn_type] = {
                    'count': row['count'],
                    'amount': float(row['total_amount'])
                }
            
            # Calculate summary statistics
            total_deposits = sum(data['deposits']['amount'] for data in daily_trends.values())
            total_withdrawals = sum(data['withdrawals']['amount'] for data in daily_trends.values())
            total_transactions = sum(
                data['deposits']['count'] + data['withdrawals']['count'] 
                for data in daily_trends.values()
            )
            
            return {
                'period_days': days,
                'daily_trends': daily_trends,
                'summary': {
                    'total_transactions': total_transactions,
                    'total_deposits': total_deposits,
                    'total_withdrawals': total_withdrawals,
                    'net_flow': total_deposits - total_withdrawals,
                    'average_daily_transactions': total_transactions / days if days > 0 else 0
                }
            }
        except Exception as e:
            return {'error': str(e)}
    
    @staticmethod
    def generate_account_statement_pdf(account_id: int, start_date: str = None, 
                                      end_date: str = None) -> Dict:
        """Generate account statement (placeholder for PDF generation)"""
        try:
            statement = TransactionManager.get_account_statement(account_id, start_date, end_date)
            
            # In a real implementation, this would generate a PDF
            # For now, we'll return the data in a structured format
            
            return {
                'statement': statement,
                'generated_at': datetime.now().isoformat(),
                'format': 'pdf_placeholder',
                'download_url': f'/api/statements/{account_id}/download'
            }
        except Exception as e:
            return {'error': str(e)}
    
    @staticmethod
    def get_customer_segmentation() -> Dict:
        """Analyze customer segmentation based on account activity"""
        try:
            # Get customer data with account information
            query = """
                SELECT 
                    c.customer_id,
                    c.first_name,
                    c.last_name,
                    c.email,
                    COUNT(a.account_id) as account_count,
                    SUM(a.balance) as total_balance,
                    COUNT(t.transaction_id) as transaction_count
                FROM customers c
                LEFT JOIN accounts a ON c.customer_id = a.customer_id AND a.status = 'ACTIVE'
                LEFT JOIN transactions t ON a.account_id = t.account_id
                GROUP BY c.customer_id, c.first_name, c.last_name, c.email
                ORDER BY total_balance DESC
            """
            
            results = db.execute_query(query)
            
            # Segment customers
            segments = {
                'high_value': [],      # Balance > ₹50,000
                'medium_value': [],    # Balance ₹10,000 - ₹50,000
                'low_value': [],       # Balance < ₹10,000
                'inactive': []         # No transactions in last 90 days
            }
            
            cutoff_date = datetime.now() - timedelta(days=90)
            
            for row in results:
                customer_data = {
                    'customer_id': row['customer_id'],
                    'name': f"{row['first_name']} {row['last_name']}",
                    'email': row['email'],
                    'account_count': row['account_count'],
                    'total_balance': float(row['total_balance'] or 0),
                    'transaction_count': row['transaction_count']
                }
                
                balance = customer_data['total_balance']
                
                if balance > 50000:  # ₹50,000
                    segments['high_value'].append(customer_data)
                elif balance >= 10000:  # ₹10,000
                    segments['medium_value'].append(customer_data)
                else:
                    segments['low_value'].append(customer_data)
            
            return {
                'segmentation': segments,
                'summary': {
                    'total_customers': len(results),
                    'high_value_count': len(segments['high_value']),
                    'medium_value_count': len(segments['medium_value']),
                    'low_value_count': len(segments['low_value'])
                }
            }
        except Exception as e:
            return {'error': str(e)}


class ReportGenerator:
    """Generate various types of reports"""
    
    @staticmethod
    def generate_monthly_report(month: str = None) -> Dict:
        """Generate monthly banking report"""
        if not month:
            month = datetime.now().strftime('%Y-%m')
        
        try:
            # Get monthly statistics
            query = """
                SELECT 
                    COUNT(DISTINCT c.customer_id) as new_customers,
                    COUNT(DISTINCT a.account_id) as new_accounts,
                    SUM(t.amount) as total_transaction_volume,
                    COUNT(t.transaction_id) as total_transactions
                FROM customers c
                LEFT JOIN accounts a ON c.customer_id = a.customer_id 
                    AND strftime('%Y-%m', a.created_at) = ?
                LEFT JOIN transactions t ON a.account_id = t.account_id 
                    AND strftime('%Y-%m', t.transaction_date) = ?
            """
            
            results = db.execute_query(query, (month, month))
            
            return {
                'month': month,
                'new_customers': results[0]['new_customers'],
                'new_accounts': results[0]['new_accounts'],
                'total_transaction_volume': float(results[0]['total_transaction_volume'] or 0),
                'total_transactions': results[0]['total_transactions'],
                'generated_at': datetime.now().isoformat()
            }
        except Exception as e:
            return {'error': str(e)}
    
    @staticmethod
    def generate_risk_assessment_report() -> Dict:
        """Generate risk assessment report"""
        try:
            # High-risk accounts (large transactions, frequent activity)
            risk_query = """
                SELECT 
                    a.account_id,
                    a.account_number,
                    c.first_name || ' ' || c.last_name as customer_name,
                    a.balance,
                    COUNT(t.transaction_id) as transaction_count,
                    MAX(t.amount) as largest_transaction,
                    SUM(t.amount) as total_volume
                FROM accounts a
                JOIN customers c ON a.customer_id = c.customer_id
                JOIN transactions t ON a.account_id = t.account_id
                WHERE a.status = 'ACTIVE'
                GROUP BY a.account_id, a.account_number, c.first_name, c.last_name, a.balance
                HAVING COUNT(t.transaction_id) > 50 OR MAX(t.amount) > 10000
                ORDER BY total_volume DESC
            """
            
            risk_accounts = db.execute_query(risk_query)
            
            return {
                'risk_assessment': {
                    'high_risk_accounts': [dict(row) for row in risk_accounts],
                    'total_high_risk': len(risk_accounts),
                    'assessment_criteria': {
                        'high_transaction_count': '> 50 transactions',
                        'large_transaction_amount': '> ₹10,000 single transaction'
                    }
                },
                'generated_at': datetime.now().isoformat()
            }
        except Exception as e:
            return {'error': str(e)}
