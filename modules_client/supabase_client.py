import os
#!/usr/bin/env python3
"""
StreamMate AI - Supabase Client Wrapper
Complete replacement for VPS server communication using Supabase
"""

import json
import requests
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import hashlib
import hmac

logger = logging.getLogger(__name__)

class SupabaseClient:
    """Complete Supabase client for StreamMate AI"""
    
    def __init__(self):
        self.config = self._load_config()
        self.base_url = self.config['url']
        self.anon_key = self.config['anon_key']
        self.service_role_key = self.config['service_role_key']
        
        # ✅ PERFORMANCE: Add simple caching to reduce repeated calculations
        self._cache = {}
        self._cache_timeout = 120  # 120 seconds cache (reduced API calls for better performance)
        
        # Headers for API requests
        self.headers = {
            'apikey': self.anon_key,
            'Authorization': f'Bearer {self.anon_key}',
            'Content-Type': 'application/json',
            'Prefer': 'return=representation'
        }
        
        # Service role headers (for admin operations)
        self.service_headers = {
            'apikey': self.service_role_key,
            'Authorization': f'Bearer {self.service_role_key}',
            'Content-Type': 'application/json',
            'Prefer': 'return=representation'
        }
        
        logger.info(f"🚀 Supabase client initialized: {self.base_url}")
    
    def _load_config(self) -> Dict[str, str]:
        """Load Supabase configuration"""
        config_path = Path("config/supabase_config.json")
        if not config_path.exists():
            raise FileNotFoundError(f"Supabase config not found: {config_path}")
        
        with open(config_path, 'r') as f:
            return json.load(f)
    
    def _make_request(self, method: str, endpoint: str, data: Dict = None, use_service_role: bool = False) -> Dict[str, Any]:
        """Make HTTP request to Supabase"""
        headers = self.service_headers if use_service_role else self.headers
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=data)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=data)
            elif method == 'PATCH':
                response = requests.patch(url, headers=headers, json=data)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, json=data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            # Handle different success status codes
            if response.status_code in [200, 201, 204]:
                # For PATCH requests, 204 means success with no content
                if method == 'PATCH' and response.status_code == 204:
                    return {"success": True, "message": "Updated successfully"}
                # For other requests, return JSON if available
                try:
                    return response.json()
                except:
                    return {"success": True, "message": "Request successful"}
            else:
                # Only raise exception for non-success status codes
                response.raise_for_status()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Supabase request failed: {e}")
            raise
    
    def validate_license(self, email: str, hardware_id: str = None) -> Dict[str, Any]:
        """Validate user license and get credit balance"""
        try:
            # Get user data from Supabase
            user_data = self.get_user_data(email)
            
            if not user_data:
                return {
                    "is_valid": False,
                    "tier": "none",
                    "message": "User not found",
                    "source": "supabase",
                    "hours_credit": 0.0
                }
            
            # Check wallet balance
            wallet_balance = float(user_data.get("wallet_balance", 0))
            basic_credits = float(user_data.get("basic_credits", 0))
            pro_credits = float(user_data.get("pro_credits", 0))
            
            # Determine tier based on credits
            if pro_credits > 0:
                tier = "pro"
                available_credits = pro_credits
            elif basic_credits > 0:
                tier = "basic"
                available_credits = basic_credits
            else:
                tier = "none"
                available_credits = 0
            
            return {
                "is_valid": available_credits > 0,
                "tier": tier,
                "message": "License validated via Supabase",
                "source": "supabase",
                "hours_credit": available_credits,
                "wallet_balance": wallet_balance,
                "basic_credits": basic_credits,
                "pro_credits": pro_credits
            }
            
        except Exception as e:
            logger.error(f"License validation failed: {e}")
            return {
                "is_valid": False,
                "tier": "none",
                "message": f"License validation failed: {str(e)}",
                "source": "supabase_error",
                "hours_credit": 0.0
            }
    
    
    def _get_cached_credits(self, email: str) -> Dict:
        """Get cached credit data to reduce database calls"""
        import time
        cache_key = f"credits_{email}"
        current_time = time.time()
        
        if (hasattr(self, '_credit_cache') and 
            cache_key in self._credit_cache and 
            current_time - self._credit_cache[cache_key]['timestamp'] < self._cache_timeout):
            
            print(f"[CACHE-HIT] Using cached credits for {email}")
            return self._credit_cache[cache_key]['data']
        
        # Cache miss - fetch fresh data
        credit_data = self.get_credit_balance(email)
        
        if not hasattr(self, '_credit_cache'):
            self._credit_cache = {}
        
        self._credit_cache[cache_key] = {
            'data': credit_data,
            'timestamp': current_time
        }
        
        print(f"[CACHE-MISS] Fetched fresh credits for {email}")
        return credit_data

    def get_credit_balance(self, email: str) -> Dict[str, Any]:
        """Get complete credit balance for user"""
        try:
            user_data = self.get_user_data(email)
            
            if not user_data:
                return {
                    "status": "error",
                    "message": "User not found",
                    "data": {
                        "email": email,
                        "wallet_balance": 0,
                        "basic_credits": 0,
                        "pro_credits": 0,
                        "total_credits": 0
                    }
                }
            
            # Use 'credits' field from user_profiles table
            wallet_credits = float(user_data.get("credits", 0))
            
            # CALCULATE Basic and Pro credits based on transaction history
            # Since database doesn't have basic_credits and pro_credits fields yet
            basic_credits = 0
            pro_credits = 0
            
            # Get transaction history to calculate credits
            try:
                transaction_url = f"{self.base_url}/rest/v1/credit_transactions?email=eq.{email}&order=created_at.desc"
                transaction_response = requests.get(transaction_url, headers=self.service_headers)
                
                if transaction_response.status_code == 200:
                    transactions = transaction_response.json()
                    
                    # Calculate credits based on transaction history - ACCUMULATE purchases and SUBTRACT deductions
                    for tx in transactions:
                        amount = float(tx.get("amount", 0))
                        description = tx.get("description", "").lower()
                        transaction_type = tx.get("transaction_type", "").lower()
                        
                        # Handle Basic mode transactions
                        if "basic" in description or "basic mode" in description:
                            if amount == 100000 and transaction_type == "credit_purchase":
                                # Credit purchase
                                basic_credits += 100000
                            elif transaction_type == "mode_usage" and amount > 0:
                                # Credit usage/deduction
                                basic_credits -= amount
                        
                        # Handle Pro mode transactions  
                        elif "pro" in description or "pro mode" in description:
                            if amount == 100000 and transaction_type == "credit_purchase":
                                # Credit purchase
                                pro_credits += 100000
                            elif transaction_type == "mode_usage" and amount > 0:
                                # Credit usage/deduction
                                pro_credits -= amount
                    
                    # ✅ PERFORMANCE: Only log if values changed to reduce spam (less frequent logging)
                    if not hasattr(self, '_last_credit_calc') or self._last_credit_calc != (basic_credits, pro_credits):
                        # Only log once per session or when values actually change
                        if not hasattr(self, '_credit_logged'):
                            print(f"[CREDIT_CALC] Found {len(transactions)} transactions")
                            print(f"[CREDIT_CALC] Basic credits: {basic_credits:,}")
                            print(f"[CREDIT_CALC] Pro credits: {pro_credits:,}")
                            self._credit_logged = True
                        self._last_credit_calc = (basic_credits, pro_credits)
                    
            except Exception as e:
                print(f"[CREDIT_CALC] Error getting transactions: {e}")
                # Fallback calculation based on wallet balance
                if wallet_credits == 200000:
                    # User has exactly 200,000 - likely purchased both Basic and Pro
                    basic_credits = 100000
                    pro_credits = 100000
                elif wallet_credits == 100000:
                    # User has 100,000 - likely purchased only Basic
                    basic_credits = 100000
                    pro_credits = 0
                elif wallet_credits == 100000:
                    # User has 100,000 - likely purchased only Pro
                    basic_credits = 0
                    pro_credits = 100000
            
            total_credits = wallet_credits + basic_credits + pro_credits
            
            return {
                "status": "success",
                "message": "Credit balance retrieved",
                "data": {
                    "email": email,
                    "wallet_balance": wallet_credits,
                    "basic_credits": basic_credits,
                    "pro_credits": pro_credits,
                    "total_credits": total_credits,
                    "last_updated": user_data.get("updated_at", datetime.now().isoformat())
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get credit balance: {e}")
            return {
                "status": "error",
                "message": f"Failed to get credit balance: {str(e)}",
                "data": {
                    "email": email,
                    "wallet_balance": 0,
                    "basic_credits": 0,
                    "pro_credits": 0,
                    "total_credits": 0
                }
            }
    
    def _invalidate_credit_cache(self, email: str):
        """Invalidate credit cache for specific user to force refresh"""
        if hasattr(self, '_credit_cache'):
            cache_key = f"credits_{email}"
            if cache_key in self._credit_cache:
                del self._credit_cache[cache_key]
                print(f"[CACHE-INVALIDATE] Credit cache cleared for {email}")
    
    def get_user_data(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user data from Supabase"""
        try:
            response = self._make_request(
                'GET',
                f"/rest/v1/user_profiles?email=eq.{email}",  # Use user_profiles table
                use_service_role=True
            )
            
            if response and len(response) > 0:
                return response[0]
            return None
            
        except Exception as e:
            logger.error(f"Failed to get user data: {e}")
            return None
    
    def create_user(self, email: str, name: str = None) -> Dict[str, Any]:
        """Create new user in Supabase"""
        try:
            user_data = {
                "email": email,
                "credits": 0,  # Use 'credits' field
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            response = self._make_request(
                'POST',
                '/rest/v1/user_profiles',  # Use user_profiles table
                user_data,
                use_service_role=True
            )
            
            return {
                "status": "success",
                "message": "User created successfully",
                "data": response[0] if response else user_data
            }
            
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            return {
                "status": "error",
                "message": f"Failed to create user: {str(e)}"
            }
    
    def add_credits(self, email: str, amount: float, credit_type: str = "credits", 
                   order_id: str = None, description: str = None) -> Dict[str, Any]:
        """Add credits to user account"""
        try:
            # Get current user data
            user_data = self.get_user_data(email)
            
            if not user_data:
                # Create user if doesn't exist
                create_result = self.create_user(email)
                if create_result["status"] != "success":
                    return create_result
                user_data = self.get_user_data(email)
            
            # Calculate new balance
            current_balance = float(user_data.get(credit_type, 0))
            new_balance = current_balance + amount
            
            # Update user credits (convert to int for database)
            update_data = {
                credit_type: int(new_balance),  # Convert to int
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            response = self._make_request(
                'PATCH',
                f"/rest/v1/user_profiles?email=eq.{email}",  # Use user_profiles table
                update_data,
                use_service_role=True
            )
            
            # Log transaction
            self._log_transaction(email, amount, "credit_add", credit_type, order_id, description)
            
            return {
                "status": "success",
                "message": f"Added {amount} credits to {credit_type}",
                "data": {
                    "email": email,
                    "credit_type": credit_type,
                    "amount_added": amount,
                    "previous_balance": current_balance,
                    "new_balance": new_balance,
                    "order_id": order_id
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to add credits: {e}")
            return {
                "status": "error",
                "message": f"Failed to add credits: {str(e)}"
            }
    
    def deduct_credits(self, email: str, amount: float, credit_type: str = "credits",
                      component: str = None, description: str = None) -> Dict[str, Any]:
        """Deduct credits from user account"""
        try:
            # Get current user data
            user_data = self.get_user_data(email)
            
            if not user_data:
                return {
                    "status": "error",
                    "message": "User not found"
                }
            
            # Check current balance
            current_balance = float(user_data.get(credit_type, 0))
            
            if current_balance < amount:
                return {
                    "status": "error",
                    "message": "Insufficient credits",
                    "data": {
                        "email": email,
                        "credit_type": credit_type,
                        "current_balance": current_balance,
                        "requested_amount": amount
                    }
                }
            
            # Calculate new balance
            new_balance = current_balance - amount
            
            # Update user credits (convert to int for database)
            update_data = {
                credit_type: int(new_balance),  # Convert to int
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            response = self._make_request(
                'PATCH',
                f"/rest/v1/user_profiles?email=eq.{email}",  # Use user_profiles table
                update_data,
                use_service_role=True
            )
            
            # Log transaction
            self._log_transaction(email, amount, "credit_deduct", credit_type, 
                                component, description, is_deduction=True)
            
            return {
                "status": "success",
                "message": f"Deducted {amount} credits from {credit_type}",
                "data": {
                    "email": email,
                    "credit_type": credit_type,
                    "amount_deducted": amount,
                    "previous_balance": current_balance,
                    "new_balance": new_balance,
                    "component": component
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to deduct credits: {e}")
            return {
                "status": "error",
                "message": f"Failed to deduct credits: {str(e)}"
            }
    
    def add_specific_credits(self, email: str, credit_type: str, amount: float, description: str = None) -> Dict[str, Any]:
        """Add credits to specific credit type (basic_credits or pro_credits)"""
        try:
            # For now, since database only has 'credits' field, we'll use transaction history
            # to track Basic and Pro credits separately
            
            # Log the transaction with specific credit type
            transaction_data = {
                'email': email,
                'transaction_type': 'credit_add',
                'amount': amount,
                'credit_type': credit_type,
                'description': description or f"Added {credit_type}",
                'created_at': datetime.now(timezone.utc).isoformat()
            }
            
            response = self._make_request(
                'POST',
                '/rest/v1/credit_transactions',
                transaction_data,
                use_service_role=True
            )
            
            return {
                "status": "success",
                "message": f"Added {amount} to {credit_type}",
                "data": {
                    "email": email,
                    "credit_type": credit_type,
                    "amount_added": amount,
                    "description": description
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to add specific credits: {e}")
            return {
                "status": "error",
                "message": f"Failed to add specific credits: {str(e)}"
            }

    def deduct_mode_credits(self, email: str, amount: float, mode: str, 
                           component: str = None, description: str = None) -> Dict[str, Any]:
        """Deduct credits from specific mode (basic/pro) credits"""
        try:
            # Determine credit type based on mode
            if mode.lower() == "basic":
                credit_type = "basic_credits"
            elif mode.lower() == "pro":
                credit_type = "pro_credits"
            else:
                # Fallback to wallet credits for unknown modes
                credit_type = "credits"
            
            # Get current credit balance
            credit_data = self.get_credit_balance(email)
            if not credit_data or credit_data.get("status") != "success":
                return {
                    "status": "error",
                    "message": "Failed to get credit balance"
                }
            
            data = credit_data.get("data", {})
            
            # Check mode-specific credits
            if mode.lower() == "basic":
                current_balance = float(data.get("basic_credits", 0))
            elif mode.lower() == "pro":
                current_balance = float(data.get("pro_credits", 0))
            else:
                current_balance = float(data.get("wallet_balance", 0))
            
            if current_balance < amount:
                return {
                    "status": "error",
                    "message": f"Insufficient {mode} credits",
                    "data": {
                        "email": email,
                        "mode": mode,
                        "credit_type": credit_type,
                        "current_balance": current_balance,
                        "requested_amount": amount
                    }
                }
            
            # For now, since database doesn't have basic_credits/pro_credits fields,
            # we'll deduct from wallet but log it as mode-specific usage
            wallet_result = self.deduct_credits(email, amount, "credits", 
                                              component, f"{mode.upper()} Mode: {description}")
            
            if wallet_result["status"] != "success":
                return wallet_result
            
            # Log mode-specific transaction
            self._log_transaction(email, amount, "mode_usage", credit_type, 
                                component, f"{mode.upper()} Mode: {description}", is_deduction=True)
            
            # ⚡ PERFORMANCE FIX: Invalidate credit cache to force refresh
            self._invalidate_credit_cache(email)
            
            return {
                "status": "success",
                "message": f"Deducted {amount} credits from {mode} mode",
                "data": {
                    "email": email,
                    "mode": mode,
                    "credit_type": credit_type,
                    "amount_deducted": amount,
                    "previous_balance": current_balance,
                    "new_balance": current_balance - amount,
                    "component": component
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to deduct mode credits: {e}")
            return {
                "status": "error",
                "message": f"Failed to deduct mode credits: {str(e)}"
            }

    def purchase_mode_credits(self, email: str, mode: str, credits_needed: float) -> Dict[str, Any]:
        """Purchase credits for specific mode (basic/pro) from wallet"""
        try:
            # Get current user data
            user_data = self.get_user_data(email)
            
            if not user_data:
                return {
                    "status": "error",
                    "message": "User not found"
                }
            
            # Use 'credits' field as wallet balance
            wallet_balance = float(user_data.get("credits", 0))
            
            if wallet_balance < credits_needed:
                return {
                    "status": "error",
                    "message": "Insufficient wallet balance",
                    "data": {
                        "email": email,
                        "wallet_balance": wallet_balance,
                        "credits_needed": credits_needed
                    }
                }
            
            # For now, just deduct from credits (since we don't have separate basic/pro credits)
            # In the future, we can add basic_credits and pro_credits fields to the database
            wallet_result = self.deduct_credits(email, credits_needed, "credits", 
                                              "mode_purchase", f"Purchase {mode} mode credits")
            
            if wallet_result["status"] != "success":
                return wallet_result
            
            # For now, we'll just deduct from wallet since the database only has 'credits' field
            # TODO: Add basic_credits and pro_credits fields to user_profiles table
            
            return {
                "status": "success",
                "message": f"Successfully purchased {credits_needed} credits for {mode} mode",
                "data": {
                    "email": email,
                    "mode": mode,
                    "credits_purchased": credits_needed,
                    "wallet_deduction": wallet_result["data"]
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to purchase mode credits: {e}")
            return {
                "status": "error",
                "message": f"Failed to purchase mode credits: {str(e)}"
            }
    
    def create_payment_transaction(self, email: str, package: str, amount: float) -> Dict[str, Any]:
        """Create payment transaction record"""
        try:
            transaction_data = {
                'email': email,
                'transaction_type': 'pending_payment',
                'package': package,
                'amount': amount,
                'credits': amount,  # 1 IDR = 1 Credit
                'order_id': f"{email}_{int(datetime.now().timestamp())}",
                'description': f"Payment for {package} package",
                'status': 'pending',
                'created_at': datetime.now(timezone.utc).isoformat()
            }
            
            response = self._make_request(
                'POST',
                '/rest/v1/payment_transactions',
                transaction_data,
                use_service_role=True
            )
            
            return {
                'status': 'success',
                'message': 'Payment transaction created',
                'data': response[0] if response else transaction_data
            }
            
        except Exception as e:
            logger.error(f"Failed to create payment transaction: {e}")
            return {
                'status': 'error',
                'message': f'Failed to create payment transaction: {str(e)}'
            }
    
    def _log_transaction(self, email: str, amount: float, transaction_type: str, 
                        credit_type: str, order_id: str = None, description: str = None,
                        is_deduction: bool = False) -> None:
        """Log credit transaction (optional - table might not exist)"""
        try:
            transaction_log = {
                'email': email,
                'transaction_type': transaction_type,
                'credit_type': credit_type,
                'amount': amount,
                'is_deduction': is_deduction,
                'order_id': order_id,
                'description': description,
                'created_at': datetime.now(timezone.utc).isoformat()
            }
            
            # Try to log transaction, but don't fail if table doesn't exist
            try:
                self._make_request(
                    'POST',
                    '/rest/v1/credit_transactions',
                    transaction_log,
                    use_service_role=True
                )
            except Exception as table_error:
                # Table might not exist, just log the error but don't fail the main operation
                logger.warning(f"Could not log transaction (table might not exist): {table_error}")
            
        except Exception as e:
            logger.error(f"Failed to log transaction: {e}")
            # Don't raise the exception - this is optional logging
    
    def get_transaction_history(self, email: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get user transaction history"""
        try:
            response = self._make_request(
                'GET',
                f"/rest/v1/credit_transactions?email=eq.{email}&order=created_at.desc&limit={limit}",
                use_service_role=True
            )
            
            return response or []
            
        except Exception as e:
            logger.error(f"Failed to get transaction history: {e}")
            return []
    
    def health_check(self) -> Dict[str, Any]:
        """Check Supabase connection health"""
        try:
            # Simple query to test connection
            response = self._make_request(
                'GET',
                '/rest/v1/users?limit=1',
                use_service_role=True
            )
            
            return {
                'status': 'success',
                'message': 'Supabase connection healthy',
                'data': {
                    'connected': True,
                    'response_time': 'OK',
                    'database': 'PostgreSQL'
                }
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                'status': 'error',
                'message': f'Health check failed: {str(e)}',
                'data': {
                    'connected': False,
                    'error': str(e)
                }
            }

    def update_user_credits_secure(self, email: str, amount: int, transaction_type: str, description: str) -> Dict[str, Any]:
        """Update user credits using secure function"""
        try:
            url = f"{self.base_url}/rest/v1/rpc/update_user_credits"
            data = {
                "user_email": email,
                "credit_amount": amount,
                "transaction_type": transaction_type,
                "description": description
            }
            
            response = requests.post(url, headers=self.service_headers, json=data)
            
            if response.status_code == 200:
                result = response.json()
                if result:
                    logger.info(f"Credits updated successfully for {email}: {amount} credits")
                    return {
                        "status": "success",
                        "message": "Credits updated successfully",
                        "data": {
                            "email": email,
                            "amount": amount,
                            "transaction_type": transaction_type,
                            "description": description
                        }
                    }
                else:
                    logger.error(f"Failed to update credits for {email}")
                    return {
                        "status": "error",
                        "message": "Failed to update credits",
                        "data": None
                    }
            else:
                logger.error(f"Error updating credits: {response.status_code} - {response.text}")
                return {
                    "status": "error",
                    "message": f"HTTP Error: {response.status_code}",
                    "data": None
                }
                
        except Exception as e:
            logger.error(f"Exception updating credits: {e}")
            return {
                "status": "error",
                "message": f"Exception: {str(e)}",
                "data": None
            }

    def process_payment_callback_secure(self, email: str, amount: int, status: str, payment_id: str) -> Dict[str, Any]:
        """Process payment callback using secure function"""
        try:
            url = f"{self.base_url}/rest/v1/rpc/process_payment_callback"
            data = {
                "user_email": email,
                "payment_amount": amount,
                "payment_status": status,
                "payment_id": payment_id
            }
            
            response = requests.post(url, headers=self.service_headers, json=data)
            
            if response.status_code == 200:
                result = response.json()
                if result:
                    logger.info(f"Payment callback processed successfully for {email}: {amount} credits")
                    return {
                        "status": "success",
                        "message": "Payment callback processed successfully",
                        "data": {
                            "email": email,
                            "amount": amount,
                            "status": status,
                            "payment_id": payment_id
                        }
                    }
                else:
                    logger.error(f"Failed to process payment callback for {email}")
                    return {
                        "status": "error",
                        "message": "Failed to process payment callback",
                        "data": None
                    }
            else:
                logger.error(f"Error processing payment callback: {response.status_code} - {response.text}")
                return {
                    "status": "error",
                    "message": f"HTTP Error: {response.status_code}",
                    "data": None
                }
                
        except Exception as e:
            logger.error(f"Exception processing payment callback: {e}")
            return {
                "status": "error",
                "message": f"Exception: {str(e)}",
                "data": None
            }

    def generate_ai_reply(self, prompt: str, timeout: int = 30) -> str:
        """Generate AI reply using Supabase Edge Function"""
        try:
            response = self.supabase.functions.invoke(
                "ai-generate",
                invoke_options={
                    "body": {"prompt": prompt},
                    "headers": {"Content-Type": "application/json"}
                }
            )
            
            if response and hasattr(response, 'data'):
                data = response.data
                if isinstance(data, dict) and "reply" in data:
                    return data["reply"]
                elif isinstance(data, str):
                    return data
            
            return None
            
        except Exception as e:
            print(f"[Supabase] AI generation error: {e}")
            return None

# Global instance
supabase_client = SupabaseClient()

def get_supabase_client() -> SupabaseClient:
    """Get global Supabase client instance"""
    return supabase_client
