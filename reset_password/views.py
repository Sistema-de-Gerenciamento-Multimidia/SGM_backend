import os
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.urls import reverse
from django.utils.timezone import now, timedelta
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from services.email_sender.send_password_reset_emails import send_password_reset_email, send_password_reset_confirmation
from users.models import CustomUser
from .serializers import RequestPasswordResetSerializer, PasswordResetConfirmationSerializer
from .models import PasswordReset


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        try:
            serializer = RequestPasswordResetSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            email = serializer.validated_data.get('email')
            user = CustomUser.objects.filter(email__exact=email).first()
            if not user:
                # Retorno de mensagem genérica para evitar que atacantes identifiquem e-mails registrados
                return Response(
                    data={
                        'success': 'Se o e-mail estiver registrado, você receberá um link para redefinir sua senha em breve.',
                    },
                    status=status.HTTP_200_OK
                )

            # Checa se uma solicitação de redefinição de senha já existe
            existing_reset = PasswordReset.objects.filter(email=email).first()
            if existing_reset:
                token_generator = PasswordResetTokenGenerator()
                token = token_generator.make_token(user)
                existing_reset.token = token
                existing_reset.created_at = now()
                existing_reset.save()
            else:
                # Gera token e salva no banco
                token_generator = PasswordResetTokenGenerator()
                token = token_generator.make_token(user)
                reset = PasswordReset(email=email, token=token)
                reset.save()
            
            # Constroi url para redefinição de senha
            relative_url = reverse('password-reset-confirmation', kwargs={'token': token})
            reset_url = f'{os.environ.get('FRONTEND_BASE_URL', )}{relative_url}'
            
            send_password_reset_email(email, reset_url)
            
            # Retorno de mensagem genérica para evitar que atacantes identifiquem e-mails registrados
            return Response(
                data={
                    'success': 'Se o e-mail estiver registrado, você receberá um link para redefinir sua senha em breve.',
                },
                status=status.HTTP_200_OK
            )
        
        except Exception as e:
            # logger.error(f'Erro no processamento do pedido de redefinição de senha: {e}')
            return Response(
                data={
                    'error': 'Ocorreu um erro ao processar sua solicitação'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class PasswordResetConfirmationView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        try:
            serializer = PasswordResetConfirmationSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            # Checa se o token ainda está valido
            token = self.kwargs.get('token')
            reset_obj = PasswordReset.objects.filter(token__exact=token).first()
            print(reset_obj)
            if not reset_obj or (now() - timedelta(hours=24)) > reset_obj.created_at:
                return Response(
                    data={
                        'error': 'Token inválido ou expirado.'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Checa se o usuário da solicitação existe e salva a nova senha
            new_password = serializer.validated_data.get('new_password')
            user = CustomUser.objects.filter(email__exact=reset_obj.email).first()
            if not user:
                return Response(
                    data={
                        'error': 'Usuário não encontrado.'
                    },
                    status=status.HTTP_404_NOT_FOUND
                )
            
            user.set_password(new_password)
            user.save()
            # Deleta o objeto referente à solicitação de redefinição de senha após a senha ser redefinida
            reset_obj.delete()
            
            # Envia email confirmando a atualização da senha
            send_password_reset_confirmation(user.email, user.name)
            
            return Response(
                data={
                    'success': "Senha atualizada com sucesso."
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            # logger.error(f'Erro no processamento do pedido de redefinição de senha: {e}')
            return Response(
                data={
                    'Ocorreu um erro ao enviar o email de confirmação de atualização de senha.'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )