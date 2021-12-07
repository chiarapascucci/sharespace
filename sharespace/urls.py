from django.urls import path 
from sharespace import views
from sharespace.views import BorrowItemView

app_name = 'sharespace'

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about_view, name = 'about'),
    path('privacy/', views.privacy_view, name='privacy_policy'),
    path('register/', views.register_view, name = 'register_profile'),
    path('faq/', views.info_view, name='info_page'),
    path('register/address', views.address_lookup_view, name = 'address_lookup'),
    path('login/', views.login, name = 'login'),
    path('change_password/', views.change_password_view, name = 'change_password'),
    path('ajax/sub_propsal/<slug:proposal_slug>/', views.ajax_sub_prop_view, name = 'sub_to_prop'),
    path('category/', views.category_list_view, name = 'category_list'),
    path('category/<slug:cat_slug>/', views.category_page_view, name = 'category_page'),
    path('category/<slug:cat_slug>/<slug:sub_cat_slug>/', views.sub_cat_page_view, name = 'sub_cat_page'),

    path('item/', views.item_list_view, name = 'item_list'),
    path('add_item/', views.AddItemView.as_view(), name = 'add_item'),
    path('item/<slug:item_slug>/', views.item_page_view, name = 'item_page'),
    path('item/<slug:item_slug>/borrow/', BorrowItemView.as_view(), name='borrow_item'),
    path('item/<slug:item_slug>/edit/', views.EditItemView.as_view(), name='edit_item'),
    path('item/<slug:item_slug>/delete/', views.ajax_delete_item, name='delete_item'),
    path('user/complete-profile/', views.CompleteProfileView.as_view(), name = 'complete_profile'),
    path('user/<slug:user_slug>/', views.user_profile_view, name='user_profile'),
    path('user/<slug:user_slug>/edit/', views.edit_profile, name = 'edit_user_info'),
    path('user/<slug:user_slug>/your-items/', views.your_items_list_view, name = 'your_items_list'),
    path('user/<slug:user_slug>/delete/', views.AccountDeletionView.as_view(), name = 'delete_account'),

    path('submit-report/<slug:subject_slug>', views.SubmitReportView.as_view(), name = 'submit_report'),

    path('purchase/', views.purchase_proposal_list_view, name = 'proposal_list'),
    path('purchase/submit/', views.SubmitPurchaseProposal.as_view(), name = 'submit_proposal'),
    path('purchase/<slug:proposal_slug>/', views.PurchaseProposalPage.as_view(), name='proposal_page'),
    path('purchase/<slug:proposal_slug>/confirm-purchased/', views.PurchasedProposalView.as_view(), name='pp-purchased'),

    path('loan/return/', views.MarkItemAsReturnedPendingApproval.as_view(), name ='return_item'),
    path('loan/<slug:loan_slug>/', views.LoanView.as_view(), name ='loan_page'),

    path('notifications/', views.notification_list_view, name='notifications_list'),
    path('notifications/<slug:notification_slug>/', views.LoanCompleteNotificationView.as_view(), name = 'notification_page'),

    path('hood/<slug:nh_slug>/', views.hood_page_view, name  ='hood_page'),

    path('search/', views.SearchView.as_view(), name = 'search'),

    path('ajax/confirm_pick-up/', views.ajax_confirm_item_pickup, name="confirm_pick_up"),
    path('ajax/load_sub_cat/', views.load_sub_cat_view, name = "ajax_load_sub_cat"),
    path('ajax/load_user_profile/', views.load_user_profile_view, name = 'load_user_profile'),
    path('ajax/sub_proposal/', views.ajax_sub_prop_view, name = 'ajax_sub_to_prop'),
    path('ajax/request_loan/', views.ajax_borrow_item_view, name = 'ajax_request_loan'),
    path('ajax/unsub_proposal/', views.ajax_unsub_prop_view, name = 'ajax_unsub_from_prop'),
    path('ajax/cancel_booking/', views.ajax_cancel_booking, name ='ajax_cancel_booking'),
    path('ajax/post-comment/', views.ajax_post_comment, name='ajax_post_comment'),
    path('ajax/delete_purchase_proposal/', views.ajax_delete_purchase_proposal, name='ajax_del_prop'),
]
