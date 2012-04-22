import base64
import datetime
import hmac
import sha
import simplejson

from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.shortcuts import render_to_response
from django.template import RequestContext
#from django.http import HttpResponseRedirect


class FormGenerator(object):
    def __init__(self, user):
        self.user = user
        self.policy_document = None
        self._find_warehouse()

    def acl(self):
        return 'public-read'

    def redirect_to(self):
        return '%s/warehouse/postback/' % (settings.SITE_ROOT,)

    def bucket_name(self):
        return self.warehouse.bucket_name

    def upload_name(self):
        # TODO(todd): maybe do something else here like timestamp?
        return '${filename}'

    def access_key(self):
        return settings.AWS_ACCESS_KEY

    def policy(self):
        self._generate_policy()
        return self.policy_document

    def signature(self):
        self._generate_policy()
        signer = hmac.new(settings.AWS_SECRET_KEY, self.policy_document, sha)
        return base64.b64encode(signer.digest())

    def _generate_policy(self):
        if self.policy_document:
            return
        # S3 wants something that isn't quite isoformat
        expiry = datetime.datetime.now() + datetime.timedelta(days=3)
        values = {'expiration': '%sZ' % (expiry.isoformat(),),
                  'conditions': [
                      {'bucket': self.bucket_name()},
                      {'acl': self.acl()},
                      {'success_action_redirect': self.redirect_to()},
                      ['starts-with', '$key', '']]}
                      #['starts-with', '$Content-Type', '']]}
        self.policy_document = base64.b64encode(simplejson.dumps(values))

    def _find_warehouse(self):
        groups = self.user.groups.all()
        self.warehouse = None
        for group in groups:
            for warehouse in group.warehouse_set.all():
                if self.warehouse:
                    raise Exception, 'You have too many warehouse associations'
                else:
                    self.warehouse = warehouse
        if not self.warehouse:
            raise Exception, 'You do not have a warehouse association'


@permission_required('warehouse.upload')
def upload(request):
    # TODO(todd): make sure they have upload access warehouse.upload
    user = User.objects.get(username=request.user)
    form = FormGenerator(user)
    return render_to_response('warehouse/upload.html', {'form': form},
		              context_instance=RequestContext(request))


def postback(request):
    pass
