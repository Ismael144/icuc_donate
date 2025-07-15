from django.urls import path
from . import views

app_name = 'web'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('pay-zakah/', views.ContributionCreateView.as_view(), {'contribution_type': 'ZAKAH'}, name='pay_zakah'),
    path('pay-sadaqa/', views.ContributionCreateView.as_view(), {'contribution_type': 'SADAQA'}, name='pay_sadaqa'),
    path('pay-projects/', views.ContributionCreateView.as_view(), {'contribution_type': 'PROJECTS'}, name='pay_projects'),
    path('contributions/<str:contribution_type>/', views.ContributionListView.as_view(), name='contribution_list'),
    path('receipt/<int:contribution_id>/', views.ReceiptView.as_view(), name='receipt'),
    path('gallery/', views.GalleryView.as_view(), name='gallery'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('statistics/', views.OverallContributionsView.as_view(), name='overall_contributions'),
    path('projects/', views.ProjectListView.as_view(), name='projects'),
    path('activities/', views.ActivityListView.as_view(), name='activities'),
] 