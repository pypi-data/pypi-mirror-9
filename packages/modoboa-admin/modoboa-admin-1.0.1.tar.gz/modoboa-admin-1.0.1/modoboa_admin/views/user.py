
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _

import reversion

from modoboa.lib.web_utils import (
    render_to_json_response, _render_to_string
)

from ..forms import ForwardForm
from ..lib import needs_mailbox
from ..models import Alias, Mailbox


@login_required
@needs_mailbox()
@reversion.create_revision()
def forward(request, tplname="modoboa_admin/forward.html"):
    mb = request.user.mailbox_set.all()[0]
    try:
        al = Alias.objects.get(address=mb.address,
                               domain__name=mb.domain.name)
    except Alias.DoesNotExist:
        al = None
    if request.method == "POST":
        form = ForwardForm(request.POST)
        error = None
        if form.is_valid():
            if al is None:
                al = Alias()
                al.address = mb.address
                al.domain = mb.domain
                al.enabled = mb.user.is_active
            intdests = []
            if form.cleaned_data["keepcopies"]:
                intdests += [mb]
            form.parse_dest()
            al.save(
                int_rcpts=intdests, ext_rcpts=form.dests, creator=request.user
            )
            return render_to_json_response(_("Forward updated"))

        return render_to_json_response(
            {'form_errors': form.errors}, status=400
        )

    form = ForwardForm()
    if al is not None:
        form.fields["dest"].initial = al.extmboxes
        try:
            al.mboxes.get(pk=mb.id)
        except Mailbox.DoesNotExist:
            pass
        else:
            form.fields["keepcopies"].initial = True
    return render_to_json_response({
        "content": _render_to_string(request, tplname, {
            "form": form
        })
    })
