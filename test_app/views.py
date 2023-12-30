from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from test_app.models import *
from test_app.serializers import *
from django.shortcuts import get_object_or_404
from rest_framework import status
from django.db.models import Subquery, OuterRef
from rest_framework.parsers import FormParser, MultiPartParser
import csv
from django.db.models import Sum



class UserLoginView(APIView):
    """
    user login API view user need to post email and password to login
    """
    def post(self, request, *args, **kwargs):
        email = request.data['email']
        password = request.data['password']
        user = authenticate(request, email=email, password=password)
        if user is not None:
            token = Token.objects.get_or_create(user=user)
            return Response({'response':{'token':token[0].key, 'user_id':token[0].user_id}})
        else:
            return Response({'error': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)
        
class UserLogoutView(APIView):
    """
    user logout API view
    """
    def post(self, request):
        request.auth.delete()
        return Response(status=status.HTTP_200_OK)


class UserDetailView(APIView):
    """
    get and update user's details API view 
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        queryset = CustomUser.objects.filter(id=id)
        if queryset is not None:
            serializer = UserLoginSerializer(queryset, many=True)
            return Response(serializer.data)
        else:
            return Response({'error': 'user not found!'}, status=status.HTTP_401_UNAUTHORIZED)
            
    def patch(self, request, id):
        queryset =get_object_or_404(CustomUser, id = id)
        serializer = UserLoginSerializer(queryset, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"result" : "User's details updated!"}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors) 


class CountryDetailView(APIView):
    '''
    get country's datials API view
    '''
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        queryset = Country.objects.all()
        # adding all cities of country in country queryset
        annotated_queryset = queryset.annotate(
            cities=Subquery(
                City.objects.filter(country=OuterRef('pk')).values_list('name', flat=True)
            )
        )
        serializer = CountrySerializer(annotated_queryset, many=True)
        
        return Response(serializer.data)

class UploadFileDetail(APIView):
       '''
       upload csv file view
       '''
       permission_classes = [IsAuthenticated]

       def post(self, request, format = 'csv'):
              file_data = request.FILES['file']
              decoded_file = file_data.read().decode('utf-8').splitlines()
              csv_reader = csv.reader(decoded_file)
              header = next(csv_reader)
              data_list = []
              for row in csv_reader:
                            data_dict = dict(zip(header, row))
                            data_list.append(data_dict)
              return Response(data_list)

class FileUploadView(APIView):
        parser_classes = (MultiPartParser, FormParser)
        serializer_class = FileUploadSerializer
        permission_classes = [IsAuthenticated]

        def post(self, request, format='csv'):
            data = request.data.copy()
            import pdb;pdb.set_trace()
            file_data = request.FILES['file']
            decoded_file = file_data.read().decode('utf-8').splitlines()
            csv_reader = csv.reader(decoded_file)
            data['uploaded_by'] = request.user.id
            serializer = self.serializer_class(data=data)
            if serializer.is_valid():
                serializer.save()
                header = next(csv_reader)
                data_list = []
                for row in csv_reader:
                        data_dict = dict(zip(header, row))
                        data_dict['created_by'] = request.user
                        data_dict['file_name'] = serializer.instance
                        data_list.append(data_dict)
                        SalesData.objects.create(**data_dict)
                return Response(serializer.data)
            else:
                return Response(serializer.errors)
            
        def patch(self, request, id):
              queryset =get_object_or_404(SalesData, id = id)
              serializer = SalesDataSerializer(queryset, data=request.data, partial=True)
              if serializer.is_valid():
                     serializer.save()
                     return Response(status=status.HTTP_200_OK)
              return Response(serializer.errors)
       
        def delete(self,request, id):
              instance = get_object_or_404(SalesData, id=id)
              instance.delete()
              return Response(status=status.HTTP_204_NO_CONTENT)


class SalesDataDetail(APIView):

       permission_classes = [IsAuthenticated]

       def get(self, request):
              sale_data = SalesData.objects.filter(created_by=request.user)
              serializer = SalesDataSerializer(sale_data, many=True)
              return Response(serializer.data)

class SalesStatisticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # a. Average sales for the user.
        current_sales_data = SalesData.objects.filter(created_by=request.user)
        current_total_revenue = current_sales_data.aggregate(Sum('revenue'))['revenue__sum'] or 0
        current_total_sales_number = current_sales_data.aggregate(Sum('sales_number'))['sales_number__sum'] or 0
        average_sales_for_current_user = current_total_revenue / current_total_sales_number if current_total_sales_number else 0

        # b. Average sales for all users.
        all_user_total_revenue = SalesData.objects.aggregate(Sum('revenue'))['revenue__sum'] or 0
        all_user_total_sales_number = SalesData.objects.aggregate(Sum('sales_number'))['sales_number__sum'] or 0
        average_sale_all_user = all_user_total_revenue / all_user_total_sales_number if all_user_total_sales_number else 0

        # c. Highest sales revenue for one sale for the user.
        highest_revenue_sale_for_current_user = current_sales_data.order_by('-revenue').first()

        # d. The product that has the highest revenue for the user.
        product_highest_revenue_for_current_user = current_sales_data.values('product').annotate(
            max_revenue=Sum('revenue')).order_by('-max_revenue').first()

        # e. The product that the user has sold the most of.
        product_highest_sales_number_for_current_user = current_sales_data.values('product').annotate(
            max_sales=Sum('sales_number')).order_by('-max_sales').first()

        final_dict = {
            "average_sales_for_current_user": average_sales_for_current_user,
            "average_sale_all_user": average_sale_all_user,
            "highest_revenue_sale_for_current_user": {
                "sale_id": highest_revenue_sale_for_current_user.id,
                "revenue": highest_revenue_sale_for_current_user.revenue
            } if highest_revenue_sale_for_current_user else None,
            "product_highest_revenue_for_current_user": {
                "product_name": product_highest_revenue_for_current_user['product'],
                "price": product_highest_revenue_for_current_user['max_revenue']
            } if product_highest_revenue_for_current_user else None,
            "product_highest_sales_number_for_current_user": {
                "product_name": product_highest_sales_number_for_current_user['product'],
                "price": product_highest_sales_number_for_current_user['max_sales']
            } if product_highest_sales_number_for_current_user else None,
        }

        return Response(final_dict)

