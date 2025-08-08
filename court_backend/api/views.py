from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import CaseInputSerializer
from .services import DelhiHighCourtScraperService

class DelhiHighCourtScraper(APIView):
    def post(self, request):
        serializer = CaseInputSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            case_type = data['case_type']
            case_number = data['case_number']
            filing_year = data['filing_year']
            
            try:
                scraper_service = DelhiHighCourtScraperService(case_type, case_number, filing_year)
                result = scraper_service.scrape()
                return Response(result)
            except Exception as e:
                return Response({"error": str(e)}, status=500)
        
        return Response(serializer.errors, status=400)