from rest_framework.pagination import PageNumberPagination


class AppPagination(PageNumberPagination):
    """
    Pagination class used across the app. Every list view uses
    pagination for better performance.
    """

    page_size = 24
    page_size_query_param = "page-size"
    max_page_size = 100


class HomePageAppPagination(PageNumberPagination):
    """
    Pagination class used across the app. Every list view uses
    pagination for better performance.
    """

    page_size = 5
    page_size_query_param = "page-size"
    max_page_size = 100

class SubscriptionPlanAppPagination(PageNumberPagination):
    """
    Pagination class used across the app. Every list view uses
    pagination for better performance.
    """

    page_size = 8
    page_size_query_param = "page-size"
    max_page_size = 100

class HomePageAppCoursePagination(PageNumberPagination):
    """
    Pagination class used across the app. Every list view uses
    pagination for better performance.
    """

    page_size = 16
    page_size_query_param = "page-size"
    max_page_size = 100