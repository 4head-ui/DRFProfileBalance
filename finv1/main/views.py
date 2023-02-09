from django.http import Http404
from rest_framework.permissions import AllowAny
from rest_framework import permissions, viewsets
from rest_framework import status,generics,views
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes,authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.contrib.auth import login, logout
from rest_framework.authentication import TokenAuthentication
from django.db import transaction
from django.db.models import F
from django.db.models.signals import post_save
from django.dispatch import receiver
import plotly.express as px

from .serializers import AtSerializer,CategorySerializer,FUSerializer,\
    RegisterSerializer,LoginSerializer,NBSerializer,CASerializer
from .models import Amounttake,FinUser,Category
from .filters import AmounttakeFilter


class TakesViewSet(viewsets.ModelViewSet):
    queryset = Amounttake.objects.all()
    serializer_class = AtSerializer
    filterset_class = AmounttakeFilter
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication,]

    def get_queryset(self):
        return Amounttake.objects.filter(user=self.request.user)


@permission_classes([IsAuthenticated,])
@authentication_classes((TokenAuthentication,))
@api_view(["GET","POST"])
def amounttake(request):
    if request.method == 'GET':
        amounttakes = Amounttake.objects.filter(user=request.user)
        serializer = AtSerializer(amounttakes,many=True)
        return Response(serializer.data)
    if request.method == 'POST':
        serializer = AtSerializer(data=request.data)
        if serializer.is_valid():
            with transaction.atomic():
                z = serializer.validated_data['amount']
                FinUser.objects.filter(username=request.user).update(account_balance=F('account_balance') + z)
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileAPI(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = [TokenAuthentication,]
    def get(self,request,*args,**kwargs):
        try:
            user = FinUser.objects.get(id=request.user.id)
            serializer = FUSerializer(user)
            return Response(serializer.data)
        except FinUser.DoesNotExist:
            raise Http404


@permission_classes([IsAuthenticated,])
@authentication_classes((TokenAuthentication,))
@api_view(['GET','PUT','PUTCH','DELETE'])
def api_amounttake_detail(request,pk):
    try:
        amounttake = Amounttake.objects.filter(user=request.user).get(pk=pk)
        if request.method == 'GET':
            serializer = AtSerializer(amounttake)
            return Response(serializer.data)
        elif request.method == 'PUT' or request.method == 'PATCH':
            serializer = AtSerializer(amounttake,data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'DELETE':
            amounttake.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
    except Amounttake.DoesNotExist:
            raise Http404


@api_view(["POST"])
def nobody_amounttake(request):
    if request.method == 'POST':
        serializer = NBSerializer(data=request.data)
        if serializer.is_valid():
            with transaction.atomic():
                z = serializer.validated_data['amount']
                FinUser.objects.filter(username=serializer.validated_data['user']).update(account_balance=F('account_balance') + z)
            serializer.save(user=serializer.validated_data['user'])
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(views.APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = LoginSerializer(data=self.request.data,
            context={'request': self.request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@authentication_classes((TokenAuthentication,))
def User_logout(request):
    logout(request)
    return Response('User Logged out successfully')


#Class based view to register user
class RegisterUserAPIView(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        token, created = Token.objects.get_or_create(user=serializer.instance)
        return Response({'token': token.key}, status=status.HTTP_201_CREATED, headers=headers)


#or bulk_create
@receiver(post_save,sender=FinUser)
def add_categories(sender,instance,created,**kwargs):
    if created:
        Category.objects.create(user=instance,
                                    category_name='Забота о себе',
                                    category_amount=0),
        Category.objects.create(user=instance,
                                    category_name='Здоровье',
                                    category_amount=0)
        Category.objects.create(user=instance,
                                category_name='Зарплата',
                                category_amount=0)
        Category.objects.create(user=instance,
                                category_name='Кафе и рестораны',
                                category_amount=0)
        Category.objects.create(user=instance,
                                category_name='Машина',
                                category_amount=0)
        Category.objects.create(user=instance,
                                category_name='Образование',
                                category_amount=0)
        Category.objects.create(user=instance,
                                category_name='Отдых и развлечения',
                                category_amount=0)
        Category.objects.create(user=instance,
                                category_name='Платежи,комиссии',
                                category_amount=0)
        Category.objects.create(user=instance,
                                category_name='Покупки: одежда, техника',
                                category_amount=0)
        Category.objects.create(user=instance,
                                category_name='Продукты',
                                category_amount=0)
        Category.objects.create(user=instance,
                                category_name='Проезд',
                                category_amount=0)


@permission_classes([IsAuthenticated,])
@authentication_classes((TokenAuthentication,))
@api_view(["GET","POST"])
def categories(request):
    if request.method == 'GET':
        categories = Category.objects.filter(user=request.user)
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAuthenticated,])
@authentication_classes((TokenAuthentication,))
@api_view(['GET','PUT','PUTCH','DELETE'])
def api_category_detail(request,pk):
    try:
        category = Category.objects.filter(user=request.user).get(pk=pk)
        if request.method == 'GET':
            serializer = CategorySerializer(category)
            return Response(serializer.data)
        elif request.method == 'PUT' or request.method == 'PATCH':
            serializer = CategorySerializer(category,data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'DELETE':
            category.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
    except Category.DoesNotExist:
        raise Http404


@permission_classes([IsAuthenticated,])
@authentication_classes((TokenAuthentication,))
@api_view(["GET","POST"])
def amount_categories(request):
    if request.method == 'GET':
        categories = Category.objects.filter(user=request.user)
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        CISserializer = CASerializer(data=request.data)
        if CISserializer.is_valid():
            z = CISserializer.validated_data['amount']
            v = CISserializer.validated_data['name_of_category']
            with transaction.atomic():
                qs_balance = FinUser.objects.filter(username=request.user).values_list('account_balance')
                for now_balance in qs_balance[0]:
                    pass
                if now_balance == 0 or now_balance < z:
                    return Response('Недостаточно средств для перевода на категорию')
                else:
                    FinUser.objects.filter(username=request.user).update(
                        account_balance=F('account_balance') - z)
                    Category.objects.filter(user=request.user,category_name=v).update\
                    (category_amount=F('category_amount') + z)
                CISserializer.save(user=request.user)
            return Response(CISserializer.data, status=status.HTTP_201_CREATED)
        return Response(CISserializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
#stat with plotly usage
@permission_classes([IsAuthenticated,])
@authentication_classes((TokenAuthentication,))
@api_view(["GET"])
def stat(request):
    category_values = []
    category_names = []
    v = Category.objects.filter(user=request.user).values_list('category_amount')
    for x in v:
        for i in x:
            category_values.append(i)
    c = Category.objects.filter(user=request.user).values_list('category_name')
    for x in c:
        for i in x:
            category_names.append(i)
    fig = px.pie(values=category_values,names=category_names)
    statistica = fig.show()
    return Response(statistica)


#статистика на основе chart.js
@login_required
def js_stat(request):
    category_values = []
    category_names = []
    v = Category.objects.filter(user=request.user).values_list('category_amount')
    for x in v:
        for i in x:
            category_values.append(i)
    c = Category.objects.filter(user=request.user).values_list('category_name')
    for x in c:
        for i in x:
            category_names.append(i)
    context = {'category_values': category_values,
               'category_names': category_names}
    return render(request,'main/basic.html',context)


