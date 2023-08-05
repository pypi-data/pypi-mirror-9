import json
import warnings
from django.http import HttpResponse
from crm.contract.models import Contract
from crm.group.models import Group


warnings.warn("Convert to Class Based Views", Warning)


def group(request, gid):
    group = Group.objects.filter(id=gid)
    data = json.dumps(group)
    return HttpResponse(data, mimetype="application/json")


def cost(request, gid):
    group = (Group.objects.filter(id=gid)[0].cost,)
    return HttpResponse(group, mimetype="application/json")


def document(request, gid):
    try:
        group = [Group.objects.filter(id=gid)[0].document.id]
    except:
        warnings.warn("Add exception type", Warning)
        group = [""]
    return HttpResponse(group, mimetype="application/json")


def get_group_by_uid(request, uid):
    gid = [Contract.objects.get(id=uid).group.id]
    return HttpResponse(gid, mimetype="application/json")
