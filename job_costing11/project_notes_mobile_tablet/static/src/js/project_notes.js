odoo.define('project_notes_mobile_tablet.project_notes', function (require) {
    'use strict';

    require('web.dom_ready');

    var state_options = $("select[name='task_id']:enabled option:not(:first)");
    $('.o_website_portal_details').on('change', "select[name='project_id']", function () {
        var select = $("select[name='task_id']");
        state_options.detach();
        var displayed_state = state_options.filter("[data-project_id="+($(this).val() || 0)+"]");
        var nb = displayed_state.appendTo(select).show().size();
        select.parent().toggle(nb>=0);
    });
    $('.o_website_portal_details').find("select[name='project_id']").change();

});
