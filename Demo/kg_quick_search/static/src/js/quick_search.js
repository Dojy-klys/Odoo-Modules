/** @odoo-module **/
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component } from "@odoo/owl";
class SystrayIcon extends Component { setup() {   super.setup(...arguments);
     this.action = useService("action");
     }
     _onClick() {
     this.action.doAction({
     type: "ir.actions.act_window",
     name: "Search",
      res_model: "quick.search.wizard",
       view_mode: "form",
       views: [[false, "form"]],
       target: "new",});
       }}SystrayIcon.template = "systray_icon";
       export const systrayItem = { Component: SystrayIcon,};
       registry.category("systray").add("SystrayIcon", systrayItem, { sequence: 1 });



//odoo.define('action_systray.actionSystray', function(require) {
//"use strict";
//
//var SystrayMenu = require('web.SystrayMenu');
//var Widget = require('web.Widget');
//
//
//var actionSystray = Widget.extend({
//    template: 'actionSystray',
//    events: {
//        'click #action_systray_search': '_gotoAction',
//    },
//
//    _gotoAction: function (ev) {
//        this.do_action('kg_quick_search.quick_search_wizard_action', {
//            clear_breadcrumbs: true,
//        });
//    },
//
//});
//
//SystrayMenu.Items.push(actionSystray);
//
//return actionSystray;
//
//});
