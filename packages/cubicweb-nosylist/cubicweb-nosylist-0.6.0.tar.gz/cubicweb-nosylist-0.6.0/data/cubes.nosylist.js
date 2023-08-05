function removeRelation(rtype, seid, oeid) {
    var d = asyncRemoteExec('remove_relation', rtype, seid, oeid);
    d.addCallback(function() {
        window.location.reload();
    });
}

$(function () {
    $(document).on('click', '.notificationComponent', function (evt) {
        var $mynode = $(evt.currentTarget);
        var eid = $mynode.data('eid');
        var d = asyncRemoteExec('toggle_nosylist', eid);
        d.addCallback(function(msg) {
            $mynode.loadxhtml(AJAX_BASE_URL, ajaxFuncArgs('render', null, 'ctxcomponents', 'notification', eid), null, 'swap');
            if (msg)
                updateMessage(msg);
        });
        return false;
    });
});

