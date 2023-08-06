# coding=utf-8

from django.views.generic.base import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http.response import HttpResponse

from smsc import constants as _constants
from smsc import models as _models


class CallbackView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(CallbackView, self).dispatch(request, *args, **kwargs)

    def post(self, request):
        message_id = request.POST.get('id')
        status_code = request.POST.get('status')
        error_code = request.POST.get('err')
        if error_code:
            status = u'{0} ({1})'.format(_constants.STATUSES[int(status_code)], _constants.ERRORS[int(error_code)])
        else:
            status = _constants.STATUSES[int(status_code)]
        message = _models.Message.objects.get(id=message_id)
        message.status = status
        message.save()
        return HttpResponse()
