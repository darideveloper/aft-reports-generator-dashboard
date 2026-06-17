import logging
from django.conf import settings
from django.core.mail import get_connection, EmailMessage
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)

class ValidateEmailView(APIView):
    # Public endpoint: exempt from session auth & CSRF for monitoring
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        token = request.query_params.get("token")
        expected_token = getattr(settings, "SMTP_TEST_TOKEN", None)
        
        # 1. Enforce Token Security
        if not expected_token:
            return Response(
                {"status": "error", "message": "SMTP_TEST_TOKEN is not configured on the server."}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
        if token != expected_token:
            return Response(
                {"status": "error", "message": "Unauthorized: Invalid or missing token."}, 
                status=status.HTTP_403_FORBIDDEN
            )
            
        destination_email = request.query_params.get("email")
        real_send = request.query_params.get("real", "false").lower() in ("true", "1", "yes")
        
        # 2. Validation
        if real_send and not destination_email:
            return Response(
                {"status": "error", "message": "Destination 'email' parameter is required for real sending."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            # 3. Connection & Credential Check
            connection = get_connection()
            # connection.open() performs the full handshake & authentication check
            connection.open()
            
            if real_send:
                # 4. Dispatch Real Email
                email = EmailMessage(
                    subject="SMTP Test Validation Email",
                    body="This is an automated test email to validate the project's SMTP settings.",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[destination_email],
                    connection=connection,
                )
                email.send()
                
            connection.close()
            
            return Response({
                "status": "success",
                "message": "SMTP connection validated successfully." + (" Test email sent." if real_send else ""),
                "emulated": not real_send
            })
            
        except Exception as e:
            logger.exception("SMTP Validation endpoint encountered an error")
            return Response({
                "status": "error",
                "message": f"SMTP Validation failed: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
