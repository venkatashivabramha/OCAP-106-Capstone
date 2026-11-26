"""
Contact views
"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from phonenumber_field.phonenumber import PhoneNumber

from authentication.models import User
from .models import Contact
from .serializers import ContactSerializer, AddContactSerializer


class ContactListView(APIView):
    """List all contacts"""
    
    def get(self, request):
        contacts = Contact.objects.filter(user=request.user).select_related('contact_user')
        serializer = ContactSerializer(contacts, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        """Add new contact"""
        serializer = AddContactSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        phone_number = serializer.validated_data['phone_number']
        contact_name = serializer.validated_data.get('contact_name', '')
        
        # Parse phone number
        try:
            phone = PhoneNumber.from_string(phone_number, region='IN')
        except Exception:
            return Response(
                {'error': 'Invalid phone number'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Find user with this phone number
        try:
            contact_user = User.objects.get(phone_number=phone)
        except User.DoesNotExist:
            return Response(
                {'error': 'User with this phone number not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Can't add yourself
        if contact_user == request.user:
            return Response(
                {'error': 'Cannot add yourself as contact'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if already exists
        contact, created = Contact.objects.get_or_create(
            user=request.user,
            contact_user=contact_user,
            defaults={'contact_name': contact_name}
        )
        
        if not created:
            return Response(
                {'error': 'Contact already exists'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response(
            ContactSerializer(contact).data,
            status=status.HTTP_201_CREATED
        )


class ContactDetailView(APIView):
    """Get, update, or delete a specific contact"""
    
    def get_object(self, request, contact_id):
        try:
            return Contact.objects.get(id=contact_id, user=request.user)
        except Contact.DoesNotExist:
            return None
    
    def get(self, request, contact_id):
        contact = self.get_object(request, contact_id)
        if not contact:
            return Response(
                {'error': 'Contact not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = ContactSerializer(contact)
        return Response(serializer.data)
    
    def patch(self, request, contact_id):
        """Update contact name"""
        contact = self.get_object(request, contact_id)
        if not contact:
            return Response(
                {'error': 'Contact not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        contact_name = request.data.get('contact_name', '')
        contact.contact_name = contact_name
        contact.save()
        
        return Response(ContactSerializer(contact).data)
    
    def delete(self, request, contact_id):
        """Remove contact"""
        contact = self.get_object(request, contact_id)
        if not contact:
            return Response(
                {'error': 'Contact not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        contact.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ContactSearchView(APIView):
    """Search users by phone number"""
    
    def get(self, request):
        phone_number = request.query_params.get('phone_number', '')
        
        if not phone_number:
            return Response(
                {'error': 'Phone number required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            phone = PhoneNumber.from_string(phone_number, region='IN')
            user = User.objects.get(phone_number=phone)
            
            # Check if already in contacts
            is_contact = Contact.objects.filter(
                user=request.user,
                contact_user=user
            ).exists()
            
            from authentication.serializers import UserSerializer
            return Response({
                'user': UserSerializer(user).data,
                'is_contact': is_contact
            })
            
        except Exception:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
