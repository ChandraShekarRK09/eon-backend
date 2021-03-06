"""
Presigned url are here
"""
import json
import os
import secrets

from rest_framework import status
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from core.models import Event
from eon_backend.settings.common import LOGGER_SERVICE, BUCKET, BUCKET_PATH
from utils.common import api_success_response, api_error_response
from utils.s3 import AwsS3

logger = LOGGER_SERVICE


class PresignedUrl(APIView):
    """
    Api for presigned url created here
    """
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        """
            :param request:
            :return:
        """
        event_id = request.GET.get('event_id')
        try:
            event = Event.objects.get(id=event_id)
        except:
            logger.log_error(f"Invalid event id {event_id} entered for getting presigned url")
            return api_error_response(message="Event is not valid", status=400)
        image_name = event.images
        bucket = BUCKET
        object_name = image_name
        s3 = AwsS3()
        presigned_url = s3.get_presigned_url(
            bucket_name=bucket,
            object_name=object_name,
            expiry=300,
        )
        return api_success_response(presigned_url, status=200)

    def post(self, request):
        """
        :param request:
        :return:
        """
        asset = json.loads(request.body)
        bucket = BUCKET
        secret = secrets.token_hex(12)
        path = BUCKET_PATH
        name = os.path.splitext(asset["path_name"])
        object_name = path + name[0] + "_" + secret + name[1]
        s3 = AwsS3()
        presigned_url = s3.put_presigned_url(
            bucket_name=bucket,
            object_name=object_name,
            expiry=300,
        )
        logger.log_info("presigned url successfully registered")
        return api_success_response(data=dict(presigned_url=presigned_url, image_name=object_name),
                                    status=status.HTTP_200_OK)
