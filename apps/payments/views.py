import stripe
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db import transaction
from .models import PaymentIntentRecord

stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', 'sk_test_placeholder')

class CreatePaymentIntentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        amount = request.data.get('amount')
        coins = request.data.get('coins')
        
        if not amount or not coins:
            return Response({"error": "Amount and coins are required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Create a PaymentIntent with the order amount and currency
            intent = stripe.PaymentIntent.create(
                amount=int(amount),
                currency='usd',
                automatic_payment_methods={
                    'enabled': True,
                },
                metadata={
                    'user_id': request.user.id,
                    'coins': coins,
                }
            )
            
            # Save a record of the intent
            PaymentIntentRecord.objects.create(
                user=request.user,
                intent_id=intent.id,
                amount=amount,
                coins_awarded=coins,
                status='pending'
            )
            
            return Response({
                'clientSecret': intent.client_secret,
                'publishableKey': getattr(settings, 'STRIPE_PUBLISHABLE_KEY', 'pk_test_placeholder')
            })
            
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class StripeWebhookView(APIView):
    authentication_classes = [] # No JWT for Stripe incoming requests
    permission_classes = [] 

    def post(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        endpoint_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', '')
        
        if not endpoint_secret:
             return Response({"error": "Webhook secret not configured"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        event = None
        
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except ValueError as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.SignatureVerificationError as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)
            
        if event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            intent_id = payment_intent['id']
            
            with transaction.atomic():
                try:
                    record = PaymentIntentRecord.objects.select_for_update().get(intent_id=intent_id, status='pending')
                    record.status = 'succeeded'
                    record.save()
                    
                    # Award coins to the user
                    user = record.user
                    user.coins += record.coins_awarded
                    user.save()
                    
                    print(f"[STRIPE] Successfully awarded {record.coins_awarded} coins to {user.username}")
                except PaymentIntentRecord.DoesNotExist:
                    print(f"[STRIPE] PaymentIntentRecord {intent_id} not found or already processed.")
                    
        return Response(status=status.HTTP_200_OK)

class ConfirmPaymentView(APIView):
    
    permission_classes = [IsAuthenticated]

    def post(self, request):
        payment_intent_id = request.data.get('payment_intent_id')
        if not payment_intent_id:
            return Response({"error": "payment_intent_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Verify with Stripe directly — cannot be spoofed by the client
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        except Exception as e:
            return Response({"error": f"Stripe error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        if intent['status'] != 'succeeded':
            return Response({"error": "Payment has not succeeded yet"}, status=status.HTTP_402_PAYMENT_REQUIRED)

        with transaction.atomic():
            try:
                record = PaymentIntentRecord.objects.select_for_update().get(
                    intent_id=payment_intent_id,
                    user=request.user,  # Ensure the record belongs to this user
                    status='pending'
                )
                record.status = 'succeeded'
                record.save()

                user = record.user
                user.coins += record.coins_awarded
                user.save()

                return Response({
                    "coins": user.coins,
                    "coins_awarded": record.coins_awarded,
                    "message": f"Successfully awarded {record.coins_awarded} coins!"
                })
            except PaymentIntentRecord.DoesNotExist:
                # Already processed — return current coin total safely
                user = request.user
                return Response({
                    "coins": user.coins,
                    "coins_awarded": 0,
                    "message": "Payment already processed."
                })

import requests

class VerifyKhaltiPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        token = request.data.get('token')
        amount = request.data.get('amount')
        coins = request.data.get('coins')

        if not token or not amount or not coins:
            return Response({"error": "Token, amount, and coins are required"}, status=status.HTTP_400_BAD_REQUEST)

        khalti_secret_key = getattr(settings, 'KHALTI_SECRET_KEY', '')
        if not khalti_secret_key:
            return Response({"error": "Khalti secret key not configured"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        payload = {
            "token": token,
            "amount": amount
        }
        headers = {
            "Authorization": f"Key {khalti_secret_key}"
        }

        try:
            # Verify with Khalti API
            response = requests.post("https://khalti.com/api/v2/payment/verify/", data=payload, headers=headers)
            response_data = response.json()

            if response.status_code == 200:
                # Payment was successful, Khalti returns state containing "idx" (transaction ID)
                khalti_idx = response_data.get('idx')

                # Ensure it's not already processed
                with transaction.atomic():
                    # Check if we already have a successful transaction for this Khalti idx
                    exists = PaymentIntentRecord.objects.filter(intent_id=khalti_idx, status='succeeded').exists()
                    if exists:
                        return Response({
                            "coins": request.user.coins,
                            "message": "Payment already processed."
                        })

                    # Record transaction and award coins
                    PaymentIntentRecord.objects.create(
                        user=request.user,
                        intent_id=khalti_idx,
                        amount=int(amount),
                        currency='npr',  # Khalti is NPR
                        coins_awarded=int(coins),
                        status='succeeded'
                    )

                    user = request.user
                    user.coins += int(coins)
                    user.save()

                    return Response({
                        "coins": user.coins,
                        "coins_awarded": int(coins),
                        "message": f"Successfully awarded {coins} coins via Khalti!"
                    })
            else:
                return Response({
                    "error": "Khalti Verification failed",
                    "details": response_data
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": f"Khalti verification error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

