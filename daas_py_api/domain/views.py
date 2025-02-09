"""
File: views.py
Description: Generic view that can be used for any domain.  It will use the configurations to control what underlying
            procedures/functions, or solr collections to read/write to.
Author: Neal Routson
Date: 2025-02-02
Version: 0.1
"""
import os
from rest_framework.views import APIView
from django.db import connection
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
from rest_framework.pagination import PageNumberPagination
from manage import logger, config
import pysolr
import json

configs = config.get_configs()
DOMAIN = os.getenv("DOMAIN").upper().strip().replace("'", "")
logger.debug(DOMAIN)
SOLR_COLLECTION = getattr(configs, f"SOLR_COLLECTION_{DOMAIN}")
SOLR_URL = f"{configs.SOLR_URL}/{SOLR_COLLECTION}"
DB_CHANNEL = getattr(configs, f"DB_CHANNEL_{DOMAIN}")
DB_PROC_GET_BY_ID = getattr(configs, f"DB_PROC_GET_BY_ID_{DOMAIN}")
DB_PROC_GET = getattr(configs, f"DB_PROC_GET_{DOMAIN}")
DB_PROC_UPSERT = getattr(configs, f"DB_PROC_UPSERT_{DOMAIN}")

logger.info (f"SOLR_URL: {SOLR_URL}")
logger.info (f"DB_CHANNEL_NAME: {DB_CHANNEL}")

# When navigating to the /api/ endpoint, we will show what API are available.
@api_view(["GET", "POST"])
def api_root(request, format=None):
    """API root view to list available endpoints."""
    return Response({
        f"{DOMAIN.lower()}-db": reverse(f"{DOMAIN.lower()}-db", request=request, format=format),
        f"{DOMAIN.lower()}-db-upsert": reverse(f"{DOMAIN.lower()}-db-upsert", request=request, format=format),
        f"{DOMAIN.lower()}-cache": reverse(f"{DOMAIN.lower()}-cache", request=request, format=format),
    })

# Class for getting all domain objects in the provided json.
class DomainDb(APIView):
    """
    Custom API view to retrieve multiple domain objects using stored procedures.
    """

    def get(self, request):
        
        """Retrieve all domain objects using a stored procedure"""
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM {DB_PROC_GET}();")
            columns = [col[0] for col in cursor.description]  # Get column names
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]  # Convert to dictionary
        
        # Apply pagination
        paginator = PageNumberPagination()
        paginator.page_size = 10  # Set the number of items per page
        paginated_results = paginator.paginate_queryset(results, request)

        # Return the paginated response
        return paginator.get_paginated_response(paginated_results)
    
    def post(self, request):
        """Retrieve multiple domain objects using a stored procedure with JSON list of IDs"""
        json_data = json.dumps(request.data)

        try:
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT * FROM {DB_PROC_GET_BY_ID}(%s);", [json_data])
                rows = cursor.fetchall()

                if rows:
                    columns = [col[0] for col in cursor.description]
                    results = [dict(zip(columns, row)) for row in rows]
                    return Response(results)

            return Response({"error": f"No {DOMAIN.lower()} found"}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            logger.error(f"Error retrieving {DOMAIN.lower()}: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Class for getting all domain objects in the provided json.
class DomainDbUpsert(APIView):
    """
    Custom API upsert multiple domain objects using stored procedures.
    """

    def get(self, request):
        
        """Retrieve all domain objects using a stored procedure"""
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM {DB_PROC_GET}();")
            columns = [col[0] for col in cursor.description]  # Get column names
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]  # Convert to dictionary
        
        # Apply pagination
        paginator = PageNumberPagination()
        paginator.page_size = 10  # Set the number of items per page
        paginated_results = paginator.paginate_queryset(results, request)

        # Return the paginated response
        return paginator.get_paginated_response(paginated_results)
    
    def post(self, request):
        """Retrieve multiple domain objects using a stored procedure with JSON list of IDs"""
        # logger.debug(f"request: {request.data}")
        
        json_data = json.dumps(request.data)

        try:

            with connection.cursor() as cursor:
                cursor.execute(f"SELECT * FROM {DB_PROC_UPSERT}(%s, %s);", [json_data, DB_CHANNEL])

                rows = cursor.fetchall()

                if rows:
                    columns = [col[0] for col in cursor.description]
                    results = [dict(zip(columns, row)) for row in rows]
                    return Response(results)

            return Response({"error": f"No {DOMAIN.lower()} found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error retrieving {DOMAIN.lower()}: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#  Class for getting all domain objects from SOLR.
class DomainCache(APIView):
    """
    API view to fetch domain objects from a SOLR instance.
    """

    def get(self, request):
        """Retrieve domain objects from SOLR."""
        solr = pysolr.Solr(SOLR_URL, always_commit=True, timeout=10)

        # Extract query parameters (if any)
        query = request.GET.get("q", "*:*")  # Default to all domain objects
        filters = request.GET.getlist("fq")  # Filter queries if provided

        # Construct SOLR search parameters
        solr_params = {
            "q": query,
            "fq": filters,  # Apply filters if provided
            "rows": 100  # Fetch up to 100 records (adjust as needed)
        }

        results = solr.search(**solr_params)
        documents = [doc for doc in results]

        # Apply pagination
        paginator = PageNumberPagination()
        paginator.page_size = 10  # Set page size
        paginated_results = paginator.paginate_queryset(documents, request)

        return paginator.get_paginated_response(paginated_results)

    def post(self, request):
        """Add a new domain objects to SOLR."""
        solr = pysolr.Solr(SOLR_URL, always_commit=True, timeout=10)
        data = request.data

        # Create document dynamically.  This requires source/target columns to be exact.
        # Ensure data is a list of dictionaries
        if isinstance(data, dict):  
            documents = [data]  # Convert single dictionary to a list
        elif isinstance(data, list):  
            documents = data  # Use as-is if it"s already a list
        else:
            return Response({"error": "Invalid input format. Expected a list or dictionary."}, status=status.HTTP_400_BAD_REQUEST)        

        # Add documents to SOLR
        solr.add(documents)

        return Response(documents, status=status.HTTP_201_CREATED)
    