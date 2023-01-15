from django.urls import path

from .views import UserProfileAPI,LoginView,\
  User_logout,categories,amounttake,nobody_amounttake,RegisterUserAPIView,\
  amount_categories,api_amounttake_detail,api_category_detail,TakesViewSet,\
  stat

app_name = 'main'

urlpatterns = [

  path('register/',RegisterUserAPIView.as_view()),
  path('login/',LoginView.as_view()),
  path('logout/',User_logout),
  path('nobody_amounttake/', nobody_amounttake),#транзакция вне логина
  path('profile/old/amount_category',amount_categories),#транзакция в логине
  path('profile/new/categories/', categories),#добавление новой категории
  path('profile/new/categories/<int:pk>/', api_category_detail),
  path('profile/new/categories/<int:pk>/', api_category_detail),
  path('profile/amounttake/', amounttake),#добавление нового пополнения счета
  path('profile/alltakes',TakesViewSet.as_view({'get': 'list'})),
  path('profile/stat',stat),#статистика на основе плотли
  #все поступления с фильтрами
  path('profile/amounttake/<int:pk>/',api_amounttake_detail),
  path('profile/', UserProfileAPI.as_view()),

]