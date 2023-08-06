this["ds"] = this["ds"] || {};
this["ds"]["templates"] = this["ds"]["templates"] || {};

this["ds"]["templates"]["edit"] = this["ds"]["templates"]["edit"] || {};

this["ds"]["templates"]["flot"] = this["ds"]["templates"]["flot"] || {};

this["ds"]["templates"]["listing"] = this["ds"]["templates"]["listing"] || {};

this["ds"]["templates"]["models"] = this["ds"]["templates"]["models"] || {};

Handlebars.registerPartial("action-menu-button", this["ds"]["templates"]["action-menu-button"] = Handlebars.template({"1":function(depth0,helpers,partials,data) {
  var stack1, helper, functionType="function", helperMissing=helpers.helperMissing, escapeExpression=this.escapeExpression, lambda=this.lambda;
  return "  <li role=\"presentation\"\n    data-ds-action=\""
    + escapeExpression(((helper = (helper = helpers.name || (depth0 != null ? depth0.name : depth0)) != null ? helper : helperMissing),(typeof helper === functionType ? helper.call(depth0, {"name":"name","hash":{},"data":data}) : helper)))
    + "\"\n    data-ds-category=\""
    + escapeExpression(((helper = (helper = helpers.category || (depth0 != null ? depth0.category : depth0)) != null ? helper : helperMissing),(typeof helper === functionType ? helper.call(depth0, {"name":"category","hash":{},"data":data}) : helper)))
    + "\"\n    data-ds-show=\""
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.action : depth0)) != null ? stack1.show : stack1), depth0))
    + "\"\n    data-ds-hide=\""
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.action : depth0)) != null ? stack1.hide : stack1), depth0))
    + "\">\n    <a role=\"menuitem\" href=\"#\"><i class=\""
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.action : depth0)) != null ? stack1.icon : stack1), depth0))
    + "\"></i> "
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.action : depth0)) != null ? stack1.display : stack1), depth0))
    + "</a>\n";
},"compiler":[6,">= 2.0.0-beta.1"],"main":function(depth0,helpers,partials,data) {
  var stack1, buffer = "";
  stack1 = helpers.each.call(depth0, (depth0 != null ? depth0.actions : depth0), {"name":"each","hash":{},"fn":this.program(1, data),"inverse":this.noop,"data":data});
  if (stack1 != null) { buffer += stack1; }
  return buffer;
},"useData":true}));

Handlebars.registerPartial("ds-action-menu", this["ds"]["templates"]["ds-action-menu"] = Handlebars.template({"compiler":[6,">= 2.0.0-beta.1"],"main":function(depth0,helpers,partials,data) {
  var stack1, helperMissing=helpers.helperMissing, escapeExpression=this.escapeExpression;
  return "<div data-ds-hide=\"edit\" class=\"btn-group\" align=\"left\">\n  <button type=\"button\"\n          class=\"btn btn-default btn-xs dropdown-toggle\"\n          data-toggle=\"dropdown\">\n    <span class=\"caret\"></span>\n  </button>\n  <ul class=\"dropdown-menu dropdown-menu-right ds-action-menu\" role=\"menu\">\n    "
    + escapeExpression(((helpers.actions || (depth0 && depth0.actions) || helperMissing).call(depth0, "presentation-transform-actions", {"name":"actions","hash":{},"data":data})))
    + "\n    "
    + escapeExpression(((helpers.actions || (depth0 && depth0.actions) || helperMissing).call(depth0, "presentation-actions", true, {"name":"actions","hash":{},"data":data})))
    + "\n    "
    + escapeExpression(((helpers.actions || (depth0 && depth0.actions) || helperMissing).call(depth0, ((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.item_type : stack1), true, {"name":"actions","hash":{},"data":data})))
    + "\n  </ul>\n</div>\n";
},"useData":true}));

Handlebars.registerPartial("ds-dashboard-listing-action-menu", this["ds"]["templates"]["ds-dashboard-listing-action-menu"] = Handlebars.template({"compiler":[6,">= 2.0.0-beta.1"],"main":function(depth0,helpers,partials,data) {
  var helper, functionType="function", helperMissing=helpers.helperMissing, escapeExpression=this.escapeExpression;
  return "<div class=\"btn-group\">\n  <button\n     type=\"button\"\n     class=\"btn btn-default btn-xs dropdown-toggle\"\n     data-toggle=\"dropdown\">\n    <span class=\"caret\"></span>\n  </button>\n  <ul class=\"dropdown-menu dropdown-menu-right ds-dashboard-action-menu\" role=\"menu\" data-ds-href=\""
    + escapeExpression(((helper = (helper = helpers.href || (depth0 != null ? depth0.href : depth0)) != null ? helper : helperMissing),(typeof helper === functionType ? helper.call(depth0, {"name":"href","hash":{},"data":data}) : helper)))
    + "\" data-ds-view-href=\""
    + escapeExpression(((helper = (helper = helpers.view_href || (depth0 != null ? depth0.view_href : depth0)) != null ? helper : helperMissing),(typeof helper === functionType ? helper.call(depth0, {"name":"view_href","hash":{},"data":data}) : helper)))
    + "\">\n\n    "
    + escapeExpression(((helpers.actions || (depth0 && depth0.actions) || helperMissing).call(depth0, "dashboard-list-actions", {"name":"actions","hash":{},"data":data})))
    + "\n  </ul>\n</div>\n";
},"useData":true}));

Handlebars.registerPartial("ds-dashboard-listing-entry", this["ds"]["templates"]["ds-dashboard-listing-entry"] = Handlebars.template({"1":function(depth0,helpers,partials,data) {
  var helper, functionType="function", helperMissing=helpers.helperMissing, escapeExpression=this.escapeExpression;
  return "            <br/>\n            <small>"
    + escapeExpression(((helper = (helper = helpers.summary || (depth0 != null ? depth0.summary : depth0)) != null ? helper : helperMissing),(typeof helper === functionType ? helper.call(depth0, {"name":"summary","hash":{},"data":data}) : helper)))
    + "</small>\n";
},"3":function(depth0,helpers,partials,data) {
  var stack1, buffer = "";
  stack1 = this.invokePartial(partials['ds-dashboard-tag-with-link'], '          ', 'ds-dashboard-tag-with-link', depth0, undefined, helpers, partials, data);
  if (stack1 != null) { buffer += stack1; }
  return buffer;
},"5":function(depth0,helpers,partials,data) {
  var helper, functionType="function", helperMissing=helpers.helperMissing, escapeExpression=this.escapeExpression;
  return "          <a href=\""
    + escapeExpression(((helper = (helper = helpers.imported_from || (depth0 != null ? depth0.imported_from : depth0)) != null ? helper : helperMissing),(typeof helper === functionType ? helper.call(depth0, {"name":"imported_from","hash":{},"data":data}) : helper)))
    + "\" target=\"_blank\"><i class=\"fa fa-cloud\"></i></a><br/>\n";
},"compiler":[6,">= 2.0.0-beta.1"],"main":function(depth0,helpers,partials,data) {
  var stack1, helper, functionType="function", helperMissing=helpers.helperMissing, escapeExpression=this.escapeExpression, buffer = "<tr data-ds-href=\""
    + escapeExpression(((helper = (helper = helpers.href || (depth0 != null ? depth0.href : depth0)) != null ? helper : helperMissing),(typeof helper === functionType ? helper.call(depth0, {"name":"href","hash":{},"data":data}) : helper)))
    + "\">\n  <td>\n    <div class=\"row\">\n      <div class=\"\"> <!-- col-md-1 -->\n        <!-- <a href=\"/dashboards/"
    + escapeExpression(((helper = (helper = helpers.id || (depth0 != null ? depth0.id : depth0)) != null ? helper : helperMissing),(typeof helper === functionType ? helper.call(depth0, {"name":"id","hash":{},"data":data}) : helper)))
    + "\"><i class=\"fa fa-2x fa-dashboard\"></i></a> -->\n      </div>\n      <div class=\"col-md-12\">\n\n        <div class=\"pull-left\">\n          <a href=\""
    + escapeExpression(((helper = (helper = helpers.view_href || (depth0 != null ? depth0.view_href : depth0)) != null ? helper : helperMissing),(typeof helper === functionType ? helper.call(depth0, {"name":"view_href","hash":{},"data":data}) : helper)))
    + "\">\n            <span class=\"ds-dashboard-listing-category\">\n              "
    + escapeExpression(((helper = (helper = helpers.category || (depth0 != null ? depth0.category : depth0)) != null ? helper : helperMissing),(typeof helper === functionType ? helper.call(depth0, {"name":"category","hash":{},"data":data}) : helper)))
    + "\n            </span>\n            <span class=\"ds-dashboard-listing-title\">\n              "
    + escapeExpression(((helper = (helper = helpers.title || (depth0 != null ? depth0.title : depth0)) != null ? helper : helperMissing),(typeof helper === functionType ? helper.call(depth0, {"name":"title","hash":{},"data":data}) : helper)))
    + "\n            </span>\n";
  stack1 = helpers['if'].call(depth0, (depth0 != null ? depth0.summary : depth0), {"name":"if","hash":{},"fn":this.program(1, data),"inverse":this.noop,"data":data});
  if (stack1 != null) { buffer += stack1; }
  buffer += "          </a><br/>\n          <span class=\"ds-dashboard-listing-last-modified\">\n            Last modified "
    + escapeExpression(((helpers.moment || (depth0 && depth0.moment) || helperMissing).call(depth0, "fromNow", (depth0 != null ? depth0.last_modified_date : depth0), {"name":"moment","hash":{},"data":data})))
    + ".\n          </span>\n        </div>\n\n        <div class=\"pull-right\" style=\"margin-left: 0.5em\">\n";
  stack1 = this.invokePartial(partials['ds-dashboard-listing-action-menu'], '          ', 'ds-dashboard-listing-action-menu', depth0, undefined, helpers, partials, data);
  if (stack1 != null) { buffer += stack1; }
  buffer += "        </div>\n\n        <div class=\"pull-right\" style=\"text-align:right\">\n";
  stack1 = helpers.each.call(depth0, (depth0 != null ? depth0.tags : depth0), {"name":"each","hash":{},"fn":this.program(3, data),"inverse":this.noop,"data":data});
  if (stack1 != null) { buffer += stack1; }
  buffer += "          <br/>\n";
  stack1 = helpers['if'].call(depth0, (depth0 != null ? depth0.imported_from : depth0), {"name":"if","hash":{},"fn":this.program(5, data),"inverse":this.noop,"data":data});
  if (stack1 != null) { buffer += stack1; }
  return buffer + "        </div>\n\n      </div>\n\n    </div> <!-- row -->\n  </td>\n</tr>\n";
},"usePartial":true,"useData":true}));

Handlebars.registerPartial("ds-dashboard-tag-with-link", this["ds"]["templates"]["ds-dashboard-tag-with-link"] = Handlebars.template({"compiler":[6,">= 2.0.0-beta.1"],"main":function(depth0,helpers,partials,data) {
  var stack1, helper, functionType="function", helperMissing=helpers.helperMissing, escapeExpression=this.escapeExpression, buffer = "<a href=\"/dashboards/tagged/"
    + escapeExpression(((helper = (helper = helpers.name || (depth0 != null ? depth0.name : depth0)) != null ? helper : helperMissing),(typeof helper === functionType ? helper.call(depth0, {"name":"name","hash":{},"data":data}) : helper)))
    + "\">";
  stack1 = this.invokePartial(partials['ds-dashboard-tag'], '', 'ds-dashboard-tag', depth0, undefined, helpers, partials, data);
  if (stack1 != null) { buffer += stack1; }
  return buffer + "</a>\n";
},"usePartial":true,"useData":true}));

Handlebars.registerPartial("ds-dashboard-tag", this["ds"]["templates"]["ds-dashboard-tag"] = Handlebars.template({"1":function(depth0,helpers,partials,data) {
  var helper, functionType="function", helperMissing=helpers.helperMissing, escapeExpression=this.escapeExpression;
  return "    background-color: "
    + escapeExpression(((helper = (helper = helpers.bgcolor || (depth0 != null ? depth0.bgcolor : depth0)) != null ? helper : helperMissing),(typeof helper === functionType ? helper.call(depth0, {"name":"bgcolor","hash":{},"data":data}) : helper)))
    + ";\n";
},"3":function(depth0,helpers,partials,data) {
  var helper, functionType="function", helperMissing=helpers.helperMissing, escapeExpression=this.escapeExpression;
  return "    color: "
    + escapeExpression(((helper = (helper = helpers.fgcolor || (depth0 != null ? depth0.fgcolor : depth0)) != null ? helper : helperMissing),(typeof helper === functionType ? helper.call(depth0, {"name":"fgcolor","hash":{},"data":data}) : helper)))
    + ";\n  ";
},"compiler":[6,">= 2.0.0-beta.1"],"main":function(depth0,helpers,partials,data) {
  var stack1, helper, functionType="function", helperMissing=helpers.helperMissing, escapeExpression=this.escapeExpression, buffer = "<span class=\"badge badge-neutral\" data-ds-tag=\""
    + escapeExpression(((helper = (helper = helpers.name || (depth0 != null ? depth0.name : depth0)) != null ? helper : helperMissing),(typeof helper === functionType ? helper.call(depth0, {"name":"name","hash":{},"data":data}) : helper)))
    + "\"\n  style=\"\n";
  stack1 = helpers['if'].call(depth0, (depth0 != null ? depth0.bgcolor : depth0), {"name":"if","hash":{},"fn":this.program(1, data),"inverse":this.noop,"data":data});
  if (stack1 != null) { buffer += stack1; }
  stack1 = helpers['if'].call(depth0, (depth0 != null ? depth0.fgcolor : depth0), {"name":"if","hash":{},"fn":this.program(3, data),"inverse":this.noop,"data":data});
  if (stack1 != null) { buffer += stack1; }
  return buffer + ">\n  \">\n  "
    + escapeExpression(((helper = (helper = helpers.name || (depth0 != null ? depth0.name : depth0)) != null ? helper : helperMissing),(typeof helper === functionType ? helper.call(depth0, {"name":"name","hash":{},"data":data}) : helper)))
    + "\n</span>\n";
},"useData":true}));

Handlebars.registerPartial("ds-edit-bar-cell", this["ds"]["templates"]["ds-edit-bar-cell"] = Handlebars.template({"compiler":[6,">= 2.0.0-beta.1"],"main":function(depth0,helpers,partials,data) {
  var stack1, lambda=this.lambda, escapeExpression=this.escapeExpression, helperMissing=helpers.helperMissing;
  return "<div class=\"ds-edit-bar ds-edit-bar-cell alert alert-info\" align=\"left\" data-ds-item-id=\""
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.item_id : stack1), depth0))
    + "\">\n  <span class=\"badge ds-badge-cell\" data-ds-item-id=\""
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.item_id : stack1), depth0))
    + "\"><i class=\"fa fa-cog\"></i> cell "
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.item_id : stack1), depth0))
    + "</span>\n  <div class=\"btn-group btn-group-sm\" data-ds-item-id=\""
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.item_id : stack1), depth0))
    + "\" style=\"display:none\">\n    "
    + escapeExpression(((helpers.actions || (depth0 && depth0.actions) || helperMissing).call(depth0, "edit-bar-cell", "button", {"name":"actions","hash":{},"data":data})))
    + "\n  </div>\n</div>\n";
},"useData":true}));

Handlebars.registerPartial("ds-edit-bar-item-details", this["ds"]["templates"]["ds-edit-bar-item-details"] = Handlebars.template({"compiler":[6,">= 2.0.0-beta.1"],"main":function(depth0,helpers,partials,data) {
  var stack1, lambda=this.lambda, escapeExpression=this.escapeExpression, buffer = "<div class=\"row\" id=\""
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.item_id : stack1), depth0))
    + "-details\">\n  <div class=\"col-md-12\">\n";
  stack1 = this.invokePartial(partials['ds-item-property-sheet'], '    ', 'ds-item-property-sheet', depth0, undefined, helpers, partials, data);
  if (stack1 != null) { buffer += stack1; }
  return buffer + "  </div>\n</div>\n";
},"usePartial":true,"useData":true}));

Handlebars.registerPartial("ds-edit-bar-item", this["ds"]["templates"]["ds-edit-bar-item"] = Handlebars.template({"compiler":[6,">= 2.0.0-beta.1"],"main":function(depth0,helpers,partials,data) {
  var stack1, lambda=this.lambda, escapeExpression=this.escapeExpression, helperMissing=helpers.helperMissing;
  return "<div class=\"row\" data-ds-show=\"edit\" style=\"display:none\">\n  <div class=\"col-md-12\">\n    <div class=\"ds-edit-bar ds-edit-bar-item\" align=\"left\" data-ds-item-id=\""
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.item_id : stack1), depth0))
    + "\">\n      <span class=\"badge ds-badge-item\" data-ds-item-id=\""
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.item_id : stack1), depth0))
    + "\"><i class=\"fa fa-cog\"></i> "
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.item_type : stack1), depth0))
    + " "
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.item_id : stack1), depth0))
    + "</span>\n      <div class=\"btn-group btn-group-sm\" data-ds-item-id=\""
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.item_id : stack1), depth0))
    + "\" style=\"display:none\">\n        "
    + escapeExpression(((helpers.actions || (depth0 && depth0.actions) || helperMissing).call(depth0, "edit-bar-item", "button", {"name":"actions","hash":{},"data":data})))
    + "\n      </div>\n    </div>\n  </div>\n</div>\n";
},"useData":true}));

Handlebars.registerPartial("ds-edit-bar-row", this["ds"]["templates"]["ds-edit-bar-row"] = Handlebars.template({"compiler":[6,">= 2.0.0-beta.1"],"main":function(depth0,helpers,partials,data) {
  var stack1, lambda=this.lambda, escapeExpression=this.escapeExpression, helperMissing=helpers.helperMissing;
  return "    <div class=\"ds-edit-bar ds-edit-bar-row\" data-ds-item-id=\""
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.item_id : stack1), depth0))
    + "\">\n      <span class=\"badge ds-badge-row\" data-ds-item-id=\""
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.item_id : stack1), depth0))
    + "\"><i class=\"fa fa-cog\"></i> row "
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.item_id : stack1), depth0))
    + "</span>\n      <div class=\"btn-group btn-group-sm\" data-ds-item-id=\""
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.item_id : stack1), depth0))
    + "\" style=\"display:none\">\n        "
    + escapeExpression(((helpers.actions || (depth0 && depth0.actions) || helperMissing).call(depth0, "edit-bar-row", "button", {"name":"actions","hash":{},"data":data})))
    + "\n      </div>\n    </div>\n";
},"useData":true}));

Handlebars.registerPartial("ds-edit-bar-section", this["ds"]["templates"]["ds-edit-bar-section"] = Handlebars.template({"compiler":[6,">= 2.0.0-beta.1"],"main":function(depth0,helpers,partials,data) {
  var stack1, lambda=this.lambda, escapeExpression=this.escapeExpression, helperMissing=helpers.helperMissing;
  return "    <div class=\"ds-edit-bar ds-edit-bar-section\" align=\"left\" data-ds-item-id=\""
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.item_id : stack1), depth0))
    + "\">\n      <span class=\"badge ds-badge-section\" data-ds-item-id=\""
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.item_id : stack1), depth0))
    + "\"><i class=\"fa fa-cog\"></i> section "
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.item_id : stack1), depth0))
    + "</span>\n      <div class=\"btn-group btn-group-sm\" data-ds-item-id=\""
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.item_id : stack1), depth0))
    + "\" style=\"display:none\">\n        "
    + escapeExpression(((helpers.actions || (depth0 && depth0.actions) || helperMissing).call(depth0, "edit-bar-section", "button", {"name":"actions","hash":{},"data":data})))
    + "\n      </div>\n    </div>\n";
},"useData":true}));

Handlebars.registerPartial("ds-edit-bar", this["ds"]["templates"]["ds-edit-bar"] = Handlebars.template({"compiler":[6,">= 2.0.0-beta.1"],"main":function(depth0,helpers,partials,data) {
  var stack1, lambda=this.lambda, escapeExpression=this.escapeExpression, helperMissing=helpers.helperMissing;
  return "<div class=\"row\" data-ds-show=\"edit\" style=\"display:none\">\n  <div class=\"col-md-12\">\n    <i title=\"Drag to reposition\" class=\"fa fa-align-justify pull-right ds-drag-handle\" data-ds-item-id=\""
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.item_id : stack1), depth0))
    + "\"></i>\n    "
    + escapeExpression(((helpers['ds-edit-bar'] || (depth0 && depth0['ds-edit-bar']) || helperMissing).call(depth0, (depth0 != null ? depth0.item : depth0), {"name":"ds-edit-bar","hash":{},"data":data})))
    + "\n  </div>\n</div>\n";
},"useData":true}));

Handlebars.registerPartial("ds-edit-menu", this["ds"]["templates"]["ds-edit-menu"] = Handlebars.template({"compiler":[6,">= 2.0.0-beta.1"],"main":function(depth0,helpers,partials,data) {
  var helperMissing=helpers.helperMissing, escapeExpression=this.escapeExpression;
  return "<div data-ds-show=\"edit\" class=\"btn-group\" align=\"left\" style=\"display:none\">\n  <button type=\"button\"\n          class=\"btn btn-default btn-xs dropdown-toggle\"\n          data-toggle=\"dropdown\">\n          <i class=\"fa fa-cog\"></i> <span class=\"caret\"></span>\n  </button>\n  <ul class=\"dropdown-menu dropdown-menu-right ds-edit-menu\" role=\"menu\">\n    "
    + escapeExpression(((helpers.actions || (depth0 && depth0.actions) || helperMissing).call(depth0, "presentation-edit", {"name":"actions","hash":{},"data":data})))
    + "\n  </ul>\n</div>\n";
},"useData":true}));

Handlebars.registerPartial("ds-preferences-renderer-entry", this["ds"]["templates"]["ds-preferences-renderer-entry"] = Handlebars.template({"1":function(depth0,helpers,partials,data) {
  return "checked=\"checked\"";
  },"compiler":[6,">= 2.0.0-beta.1"],"main":function(depth0,helpers,partials,data) {
  var stack1, helper, lambda=this.lambda, escapeExpression=this.escapeExpression, functionType="function", helperMissing=helpers.helperMissing, buffer = "<div class=\"radio\">\n  <label for=\"chartRenderRadios-"
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.renderer : depth0)) != null ? stack1.name : stack1), depth0))
    + "\">\n    <input type=\"radio\"\n           name=\"chartRenderRadios\"\n           id=\"chartRenderRadios-"
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.renderer : depth0)) != null ? stack1.name : stack1), depth0))
    + "\"\n           value=\""
    + escapeExpression(((helper = (helper = helpers.name || (depth0 != null ? depth0.name : depth0)) != null ? helper : helperMissing),(typeof helper === functionType ? helper.call(depth0, {"name":"name","hash":{},"data":data}) : helper)))
    + "\"\n           ";
  stack1 = helpers['if'].call(depth0, (depth0 != null ? depth0.checked : depth0), {"name":"if","hash":{},"fn":this.program(1, data),"inverse":this.noop,"data":data});
  if (stack1 != null) { buffer += stack1; }
  return buffer + "\n           onclick=\"dsSetPref('renderer', '"
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.renderer : depth0)) != null ? stack1.name : stack1), depth0))
    + "')\">\n    "
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.renderer : depth0)) != null ? stack1.name : stack1), depth0))
    + "\n  </label>\n  <p><small>"
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.renderer : depth0)) != null ? stack1.description : stack1), depth0))
    + "</small></p>\n</div>\n";
},"useData":true}));

Handlebars.registerPartial("ds-row-edit-bar", this["ds"]["templates"]["ds-row-edit-bar"] = Handlebars.template({"compiler":[6,">= 2.0.0-beta.1"],"main":function(depth0,helpers,partials,data) {
  return "<div class=\"row\" data-ds-show=\"edit\">\n  <div class=\"col-md-12\">\n    <div class=\"ds-edit-bar ds-row-edit-bar bs-callout bs-callout-info\">\n\n\n\n\n      row <i class=\"fa fa-trash-o pull-right\"></i>\n\n\n\n    </div>\n  </div>\n</div>\n";
  },"useData":true}));

Handlebars.registerPartial("ds-title-bar", this["ds"]["templates"]["ds-title-bar"] = Handlebars.template({"1":function(depth0,helpers,partials,data) {
  var stack1, lambda=this.lambda, escapeExpression=this.escapeExpression;
  return "<h3>"
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.title : stack1), depth0))
    + "</h3>";
},"compiler":[6,">= 2.0.0-beta.1"],"main":function(depth0,helpers,partials,data) {
  var stack1, helperMissing=helpers.helperMissing, escapeExpression=this.escapeExpression, buffer = escapeExpression(((helpers['ds-edit-bar'] || (depth0 && depth0['ds-edit-bar']) || helperMissing).call(depth0, (depth0 != null ? depth0.item : depth0), {"name":"ds-edit-bar","hash":{},"data":data})))
    + "\n<div class=\"row\">\n  <div class=\"col-md-10\">\n    ";
  stack1 = helpers['if'].call(depth0, ((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.title : stack1), {"name":"if","hash":{},"fn":this.program(1, data),"inverse":this.noop,"data":data});
  if (stack1 != null) { buffer += stack1; }
  buffer += "\n  </div>\n  <div class=\"col-md-2\" align=\"right\">\n";
  stack1 = this.invokePartial(partials['ds-action-menu'], '    ', 'ds-action-menu', depth0, undefined, helpers, partials, data);
  if (stack1 != null) { buffer += stack1; }
  return buffer + "  </div>\n</div>\n";
},"usePartial":true,"useData":true}));

Handlebars.registerPartial("dashboard-metadata-panel", this["ds"]["templates"]["edit"]["dashboard-metadata-panel"] = Handlebars.template({"1":function(depth0,helpers,partials,data) {
  var stack1, buffer = "";
  stack1 = this.invokePartial(partials['ds-dashboard-tag'], '            ', 'ds-dashboard-tag', depth0, undefined, helpers, partials, data);
  if (stack1 != null) { buffer += stack1; }
  return buffer;
},"3":function(depth0,helpers,partials,data) {
  var helper, functionType="function", helperMissing=helpers.helperMissing, escapeExpression=this.escapeExpression;
  return "          <tr>\n            <th>Imported From</th><td class=\"ds-editable\" id=ds-info-panel-edit-imported-from\" data-type=\"text\"><a href=\""
    + escapeExpression(((helper = (helper = helpers.imported_from || (depth0 != null ? depth0.imported_from : depth0)) != null ? helper : helperMissing),(typeof helper === functionType ? helper.call(depth0, {"name":"imported_from","hash":{},"data":data}) : helper)))
    + "\" target=\"_blank\">Link</a></td>\n          </tr>\n";
},"compiler":[6,">= 2.0.0-beta.1"],"main":function(depth0,helpers,partials,data) {
  var stack1, helper, functionType="function", helperMissing=helpers.helperMissing, escapeExpression=this.escapeExpression, buffer = "<div class=\"row ds-info-edit-panel\">\n  <!-- Column 1 -->\n  <div class=\"col-md-5\">\n    <h4>Properties</h4>\n\n    <table class=\"table-condensed\">\n      <tbody>\n        <tr>\n          <th>Title</th><td class=\"ds-editable\" id=\"ds-info-panel-edit-title\" data-type=\"text\">"
    + escapeExpression(((helper = (helper = helpers.title || (depth0 != null ? depth0.title : depth0)) != null ? helper : helperMissing),(typeof helper === functionType ? helper.call(depth0, {"name":"title","hash":{},"data":data}) : helper)))
    + "</td>\n        </tr>\n\n        <tr>\n          <th>Category</th><td class=\"ds-editable\" id=\"ds-info-panel-edit-category\" data-type=\"text\">"
    + escapeExpression(((helper = (helper = helpers.category || (depth0 != null ? depth0.category : depth0)) != null ? helper : helperMissing),(typeof helper === functionType ? helper.call(depth0, {"name":"category","hash":{},"data":data}) : helper)))
    + "</td>\n        </tr>\n\n        <tr>\n          <th>Summary</th><td class=\"ds-editable\" id=\"ds-info-panel-edit-summary\" data-type=\"text\">"
    + escapeExpression(((helper = (helper = helpers.summary || (depth0 != null ? depth0.summary : depth0)) != null ? helper : helperMissing),(typeof helper === functionType ? helper.call(depth0, {"name":"summary","hash":{},"data":data}) : helper)))
    + "</td>\n        </tr>\n\n        <tr>\n          <th>Tags</th>\n          <td>\n            <!--\n";
  stack1 = helpers.each.call(depth0, (depth0 != null ? depth0.tags : depth0), {"name":"each","hash":{},"fn":this.program(1, data),"inverse":this.noop,"data":data});
  if (stack1 != null) { buffer += stack1; }
  buffer += "            -->\n\n            <input id=\"ds-info-panel-edit-tags\" class=\"form-control tm-input tm-input-success tm-input-info\"/>\n\n          </td>\n        </tr>\n\n        <tr>\n          <th>Created</th><td>"
    + escapeExpression(((helpers.moment || (depth0 && depth0.moment) || helperMissing).call(depth0, "MMMM Do YYYY, h:mm:ss a", (depth0 != null ? depth0.creation_date : depth0), {"name":"moment","hash":{},"data":data})))
    + "</td>\n        </tr>\n        <tr>\n          <th>Last Modified</th><td>"
    + escapeExpression(((helpers.moment || (depth0 && depth0.moment) || helperMissing).call(depth0, "MMMM Do YYYY, h:mm:ss a", (depth0 != null ? depth0.last_modified_date : depth0), {"name":"moment","hash":{},"data":data})))
    + "</td>\n        </tr>\n\n";
  stack1 = helpers['if'].call(depth0, (depth0 != null ? depth0.imported_from : depth0), {"name":"if","hash":{},"fn":this.program(3, data),"inverse":this.noop,"data":data});
  if (stack1 != null) { buffer += stack1; }
  return buffer + "\n      </tbody>\n    </table>\n  </div> <!-- column -->\n\n  <!-- Column 2 -->\n  <div class=\"col-md-7\">\n    <h4>Description</h4>\n    <div class=\"ds-editable\"\n         id=\"ds-info-panel-edit-description\"\n         data-type=\"textarea\"\n         data-rows=\"9\"\n         data-showbuttons=\"bottom\"\n         data-inputclass=\"ds-dashboard-description\"\n         style=\"text-align:top;\">\n      "
    + escapeExpression(((helpers.markdown || (depth0 && depth0.markdown) || helperMissing).call(depth0, (depth0 != null ? depth0.description : depth0), {"name":"markdown","hash":{},"data":data})))
    + "\n    </div>\n  </div>\n\n</div>\n";
},"usePartial":true,"useData":true}));

Handlebars.registerPartial("dashboard-query-panel", this["ds"]["templates"]["edit"]["dashboard-query-panel"] = Handlebars.template({"1":function(depth0,helpers,partials,data) {
  var stack1, buffer = "";
  stack1 = this.invokePartial(partials['dashboard-query-row'], '          ', 'dashboard-query-row', depth0, undefined, helpers, partials, data);
  if (stack1 != null) { buffer += stack1; }
  return buffer;
},"compiler":[6,">= 2.0.0-beta.1"],"main":function(depth0,helpers,partials,data) {
  var stack1, helperMissing=helpers.helperMissing, escapeExpression=this.escapeExpression, buffer = "<div class=\"ds-query-edit-panel\" id=\"ds-query-panel\">\n\n  <div class=\"row\">\n    <div class=\"col-md-12\">\n      <div class=\"btn-group btn-group-sm\">\n        "
    + escapeExpression(((helpers.actions || (depth0 && depth0.actions) || helperMissing).call(depth0, "dashboard-queries", "button", {"name":"actions","hash":{},"data":data})))
    + "\n      </div>\n      <br/>\n    </div>\n  </div>\n\n  <div class=\"row\">\n    <div class=\"col-md-12\">\n      <table class=\"table table-striped\">\n";
  stack1 = helpers.each.call(depth0, ((stack1 = (depth0 != null ? depth0.definition : depth0)) != null ? stack1.queries : stack1), {"name":"each","hash":{},"fn":this.program(1, data),"inverse":this.noop,"data":data});
  if (stack1 != null) { buffer += stack1; }
  return buffer + "      </table>\n    </div>\n  </div>\n\n</div>\n";
},"usePartial":true,"useData":true}));

Handlebars.registerPartial("dashboard-query-row", this["ds"]["templates"]["edit"]["dashboard-query-row"] = Handlebars.template({"compiler":[6,">= 2.0.0-beta.1"],"main":function(depth0,helpers,partials,data) {
  var helper, functionType="function", helperMissing=helpers.helperMissing, escapeExpression=this.escapeExpression;
  return "<tr data-ds-query-name=\""
    + escapeExpression(((helper = (helper = helpers.name || (depth0 != null ? depth0.name : depth0)) != null ? helper : helperMissing),(typeof helper === functionType ? helper.call(depth0, {"name":"name","hash":{},"data":data}) : helper)))
    + "\">\n  <th data-ds-query-name=\""
    + escapeExpression(((helper = (helper = helpers.name || (depth0 != null ? depth0.name : depth0)) != null ? helper : helperMissing),(typeof helper === functionType ? helper.call(depth0, {"name":"name","hash":{},"data":data}) : helper)))
    + "\" class=\"ds-query-name\">"
    + escapeExpression(((helper = (helper = helpers.name || (depth0 != null ? depth0.name : depth0)) != null ? helper : helperMissing),(typeof helper === functionType ? helper.call(depth0, {"name":"name","hash":{},"data":data}) : helper)))
    + "</th>\n  <td data-ds-query-name=\""
    + escapeExpression(((helper = (helper = helpers.name || (depth0 != null ? depth0.name : depth0)) != null ? helper : helperMissing),(typeof helper === functionType ? helper.call(depth0, {"name":"name","hash":{},"data":data}) : helper)))
    + "\" class=\"ds-query-target\">"
    + escapeExpression(((helper = (helper = helpers.targets || (depth0 != null ? depth0.targets : depth0)) != null ? helper : helperMissing),(typeof helper === functionType ? helper.call(depth0, {"name":"targets","hash":{},"data":data}) : helper)))
    + "</td>\n  <td>\n    <div class=\"btn-group\">\n      <button class=\"btn btn-default btn-small ds-duplicate-query-button\"\n              data-toggle=\"tooltip\"\n              title=\"Duplicate this query\"\n              data-ds-query-name=\""
    + escapeExpression(((helper = (helper = helpers.name || (depth0 != null ? depth0.name : depth0)) != null ? helper : helperMissing),(typeof helper === functionType ? helper.call(depth0, {"name":"name","hash":{},"data":data}) : helper)))
    + "\">\n        <i class=\"fa fa-copy\"></i>\n      </button>\n      <button class=\"btn btn-default btn-small ds-delete-query-button\"\n              data-toggle=\"tooltip\"\n              title=\"Delete this query\"\n              data-ds-query-name=\""
    + escapeExpression(((helper = (helper = helpers.name || (depth0 != null ? depth0.name : depth0)) != null ? helper : helperMissing),(typeof helper === functionType ? helper.call(depth0, {"name":"name","hash":{},"data":data}) : helper)))
    + "\">\n        <i class=\"fa fa-trash-o\"></i>\n      </button>\n    </div>\n  </td>\n</tr>\n";
},"useData":true}));

Handlebars.registerPartial("ds-item-property-sheet", this["ds"]["templates"]["edit"]["ds-item-property-sheet"] = Handlebars.template({"1":function(depth0,helpers,partials,data,depths) {
  var stack1, helper, functionType="function", helperMissing=helpers.helperMissing, escapeExpression=this.escapeExpression, buffer = "      <tr>\n        <td><span class=\"ds-property-category\">";
  stack1 = helpers['if'].call(depth0, (depth0 != null ? depth0.category : depth0), {"name":"if","hash":{},"fn":this.program(2, data, depths),"inverse":this.noop,"data":data});
  if (stack1 != null) { buffer += stack1; }
  return buffer + "<span class=\"ds-property-name\">"
    + escapeExpression(((helper = (helper = helpers.name || (depth0 != null ? depth0.name : depth0)) != null ? helper : helperMissing),(typeof helper === functionType ? helper.call(depth0, {"name":"name","hash":{},"data":data}) : helper)))
    + "</span></td>\n        <td data-ds-property-name=\""
    + escapeExpression(((helper = (helper = helpers.name || (depth0 != null ? depth0.name : depth0)) != null ? helper : helperMissing),(typeof helper === functionType ? helper.call(depth0, {"name":"name","hash":{},"data":data}) : helper)))
    + "\">"
    + escapeExpression(((helpers.interactive_property || (depth0 && depth0.interactive_property) || helperMissing).call(depth0, depth0, (depths[1] != null ? depths[1].item : depths[1]), {"name":"interactive_property","hash":{},"data":data})))
    + "</td>\n      </tr>\n";
},"2":function(depth0,helpers,partials,data) {
  var helper, functionType="function", helperMissing=helpers.helperMissing, escapeExpression=this.escapeExpression;
  return escapeExpression(((helper = (helper = helpers.category || (depth0 != null ? depth0.category : depth0)) != null ? helper : helperMissing),(typeof helper === functionType ? helper.call(depth0, {"name":"category","hash":{},"data":data}) : helper)))
    + "</span> / ";
},"compiler":[6,">= 2.0.0-beta.1"],"main":function(depth0,helpers,partials,data,depths) {
  var stack1, buffer = "<table class=\"ds-property-sheet\">\n  <tbody>\n    <tr><th>Property</th><th>Value</th></tr>\n";
  stack1 = helpers.each.call(depth0, ((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.interactive_properties : stack1), {"name":"each","hash":{},"fn":this.program(1, data, depths),"inverse":this.noop,"data":data});
  if (stack1 != null) { buffer += stack1; }
  return buffer + "  </tbody>\n</table>\n";
},"useData":true,"useDepths":true}));

this["ds"]["templates"]["action-menu-button"] = Handlebars.template({"1":function(depth0,helpers,partials,data) {
  var stack1, buffer = "";
  stack1 = helpers['if'].call(depth0, (depth0 != null ? depth0.divider : depth0), {"name":"if","hash":{},"fn":this.program(2, data),"inverse":this.program(4, data),"data":data});
  if (stack1 != null) { buffer += stack1; }
  return buffer;
},"2":function(depth0,helpers,partials,data) {
  var helper, functionType="function", helperMissing=helpers.helperMissing, escapeExpression=this.escapeExpression;
  return "        <li class=\"divider\" data-ds-show=\""
    + escapeExpression(((helper = (helper = helpers.show || (depth0 != null ? depth0.show : depth0)) != null ? helper : helperMissing),(typeof helper === functionType ? helper.call(depth0, {"name":"show","hash":{},"data":data}) : helper)))
    + "\" data-ds-hide=\""
    + escapeExpression(((helper = (helper = helpers.hide || (depth0 != null ? depth0.hide : depth0)) != null ? helper : helperMissing),(typeof helper === functionType ? helper.call(depth0, {"name":"hide","hash":{},"data":data}) : helper)))
    + "\"/>\n";
},"4":function(depth0,helpers,partials,data) {
  var helper, functionType="function", helperMissing=helpers.helperMissing, escapeExpression=this.escapeExpression;
  return "        <li class=\""
    + escapeExpression(((helper = (helper = helpers['class'] || (depth0 != null ? depth0['class'] : depth0)) != null ? helper : helperMissing),(typeof helper === functionType ? helper.call(depth0, {"name":"class","hash":{},"data":data}) : helper)))
    + "\"\n          role=\"presentation\"\n          data-ds-action=\""
    + escapeExpression(((helper = (helper = helpers.name || (depth0 != null ? depth0.name : depth0)) != null ? helper : helperMissing),(typeof helper === functionType ? helper.call(depth0, {"name":"name","hash":{},"data":data}) : helper)))
    + "\"\n          data-ds-category=\""
    + escapeExpression(((helper = (helper = helpers.category || (depth0 != null ? depth0.category : depth0)) != null ? helper : helperMissing),(typeof helper === functionType ? helper.call(depth0, {"name":"category","hash":{},"data":data}) : helper)))
    + "\"\n          data-ds-show=\""
    + escapeExpression(((helper = (helper = helpers.show || (depth0 != null ? depth0.show : depth0)) != null ? helper : helperMissing),(typeof helper === functionType ? helper.call(depth0, {"name":"show","hash":{},"data":data}) : helper)))
    + "\"\n          data-ds-hide=\""
    + escapeExpression(((helper = (helper = helpers.hide || (depth0 != null ? depth0.hide : depth0)) != null ? helper : helperMissing),(typeof helper === functionType ? helper.call(depth0, {"name":"hide","hash":{},"data":data}) : helper)))
    + "\">\n          <a role=\"menuitem\" href=\"#\"><i class=\"fa-fw "
    + escapeExpression(((helper = (helper = helpers.icon || (depth0 != null ? depth0.icon : depth0)) != null ? helper : helperMissing),(typeof helper === functionType ? helper.call(depth0, {"name":"icon","hash":{},"data":data}) : helper)))
    + "\"></i> "
    + escapeExpression(((helper = (helper = helpers.display || (depth0 != null ? depth0.display : depth0)) != null ? helper : helperMissing),(typeof helper === functionType ? helper.call(depth0, {"name":"display","hash":{},"data":data}) : helper)))
    + "</a>\n        </li>\n";
},"compiler":[6,">= 2.0.0-beta.1"],"main":function(depth0,helpers,partials,data) {
  var stack1, lambda=this.lambda, escapeExpression=this.escapeExpression, buffer = "<div class=\"btn-group btn-group-sm\" align=\"left\">\n  <button type=\"button\"\n    class=\"btn btn-default dropdown-toggle "
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.action : depth0)) != null ? stack1['class'] : stack1), depth0))
    + "\"\n    data-toggle=\"dropdown\"\n    title=\""
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.action : depth0)) != null ? stack1.display : stack1), depth0))
    + "\">\n    <i class=\""
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.action : depth0)) != null ? stack1.icon : stack1), depth0))
    + "\"></i> <span class=\"caret\"></span>\n  </button>\n  <ul class=\"dropdown-menu dropdown-menu-left ds-edit-menu\" role=\"menu\">\n";
  stack1 = helpers.each.call(depth0, ((stack1 = (depth0 != null ? depth0.action : depth0)) != null ? stack1.actions : stack1), {"name":"each","hash":{},"fn":this.program(1, data),"inverse":this.noop,"data":data});
  if (stack1 != null) { buffer += stack1; }
  return buffer + "  </ul>\n</div>\n";
},"useData":true});

this["ds"]["templates"]["action"] = Handlebars.template({"1":function(depth0,helpers,partials,data) {
  var stack1, lambda=this.lambda, escapeExpression=this.escapeExpression;
  return "  <li class=\"divider\" data-ds-show=\""
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.action : depth0)) != null ? stack1.show : stack1), depth0))
    + "\" data-ds-hide=\""
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.action : depth0)) != null ? stack1.hide : stack1), depth0))
    + "\"/>\n";
},"3":function(depth0,helpers,partials,data) {
  var stack1, helper, lambda=this.lambda, escapeExpression=this.escapeExpression, functionType="function", helperMissing=helpers.helperMissing;
  return "  <li role=\"presentation\"\n    data-ds-action=\""
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.action : depth0)) != null ? stack1.name : stack1), depth0))
    + "\"\n    data-ds-category=\""
    + escapeExpression(((helper = (helper = helpers.category || (depth0 != null ? depth0.category : depth0)) != null ? helper : helperMissing),(typeof helper === functionType ? helper.call(depth0, {"name":"category","hash":{},"data":data}) : helper)))
    + "\"\n    data-ds-show=\""
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.action : depth0)) != null ? stack1.show : stack1), depth0))
    + "\"\n    data-ds-hide=\""
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.action : depth0)) != null ? stack1.hide : stack1), depth0))
    + "\">\n    <a role=\"menuitem\" href=\"#\"><i class=\""
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.action : depth0)) != null ? stack1.icon : stack1), depth0))
    + "\"></i> "
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.action : depth0)) != null ? stack1.display : stack1), depth0))
    + "</a>\n  </li>\n";
},"compiler":[6,">= 2.0.0-beta.1"],"main":function(depth0,helpers,partials,data) {
  var stack1, buffer = "";
  stack1 = helpers['if'].call(depth0, ((stack1 = (depth0 != null ? depth0.action : depth0)) != null ? stack1.divider : stack1), {"name":"if","hash":{},"fn":this.program(1, data),"inverse":this.program(3, data),"data":data});
  if (stack1 != null) { buffer += stack1; }
  return buffer;
},"useData":true});

this["ds"]["templates"]["action_button"] = Handlebars.template({"1":function(depth0,helpers,partials,data) {
  return "";
},"3":function(depth0,helpers,partials,data) {
  var stack1, helper, lambda=this.lambda, escapeExpression=this.escapeExpression, functionType="function", helperMissing=helpers.helperMissing, buffer = "  <button class=\"btn ";
  stack1 = helpers['if'].call(depth0, ((stack1 = (depth0 != null ? depth0.action : depth0)) != null ? stack1['class'] : stack1), {"name":"if","hash":{},"fn":this.program(4, data),"inverse":this.program(6, data),"data":data});
  if (stack1 != null) { buffer += stack1; }
  return buffer + "\"\n    data-ds-action=\""
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.action : depth0)) != null ? stack1.name : stack1), depth0))
    + "\"\n    data-ds-category=\""
    + escapeExpression(((helper = (helper = helpers.category || (depth0 != null ? depth0.category : depth0)) != null ? helper : helperMissing),(typeof helper === functionType ? helper.call(depth0, {"name":"category","hash":{},"data":data}) : helper)))
    + "\"\n    data-ds-show=\""
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.action : depth0)) != null ? stack1.show : stack1), depth0))
    + "\"\n    data-ds-hide=\""
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.action : depth0)) != null ? stack1.hide : stack1), depth0))
    + "\"\n    data-toggle=\"tooltip\"\n    title=\""
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.action : depth0)) != null ? stack1.display : stack1), depth0))
    + "\">\n    <i class=\""
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.action : depth0)) != null ? stack1.icon : stack1), depth0))
    + "\"></i>\n  </button>\n";
},"4":function(depth0,helpers,partials,data) {
  var stack1, lambda=this.lambda, escapeExpression=this.escapeExpression;
  return escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.action : depth0)) != null ? stack1['class'] : stack1), depth0));
  },"6":function(depth0,helpers,partials,data) {
  return "btn-default";
  },"compiler":[6,">= 2.0.0-beta.1"],"main":function(depth0,helpers,partials,data) {
  var stack1, buffer = "";
  stack1 = helpers['if'].call(depth0, ((stack1 = (depth0 != null ? depth0.action : depth0)) != null ? stack1.divider : stack1), {"name":"if","hash":{},"fn":this.program(1, data),"inverse":this.program(3, data),"data":data});
  if (stack1 != null) { buffer += stack1; }
  return buffer;
},"useData":true});

this["ds"]["templates"]["edit"]["dashboard_panel"] = Handlebars.template({"compiler":[6,">= 2.0.0-beta.1"],"main":function(depth0,helpers,partials,data) {
  var stack1, buffer = "<ul class=\"nav nav-pills\">\n  <li class=\"active\"><a href=\"#metadata\" data-toggle=\"tab\">Metadata</a></li>\n  <li><a href=\"#queries\" data-toggle=\"tab\" id=\"ds-edit-tab-queries\">Queries</a></li>\n</ul>\n\n<div class=\"tab-content\">\n  <div class=\"tab-pane active\" id=\"metadata\">\n";
  stack1 = this.invokePartial(partials['dashboard-metadata-panel'], '    ', 'dashboard-metadata-panel', depth0, undefined, helpers, partials, data);
  if (stack1 != null) { buffer += stack1; }
  buffer += "  </div>\n  <div class=\"tab-pane\" id=\"queries\">\n";
  stack1 = this.invokePartial(partials['dashboard-query-panel'], '    ', 'dashboard-query-panel', depth0, undefined, helpers, partials, data);
  if (stack1 != null) { buffer += stack1; }
  return buffer + "  </div>\n\n</div>\n";
},"usePartial":true,"useData":true});

this["ds"]["templates"]["edit"]["item_source"] = Handlebars.template({"compiler":[6,">= 2.0.0-beta.1"],"main":function(depth0,helpers,partials,data) {
  var helperMissing=helpers.helperMissing, escapeExpression=this.escapeExpression;
  return "<div class=\"ds-item-source\">\n  <pre>"
    + escapeExpression(((helpers.json || (depth0 && depth0.json) || helperMissing).call(depth0, (depth0 != null ? depth0.item : depth0), {"name":"json","hash":{},"data":data})))
    + "</pre>\n</div>\n";
},"useData":true});

this["ds"]["templates"]["flot"]["discrete_bar_tooltip"] = Handlebars.template({"compiler":[6,">= 2.0.0-beta.1"],"main":function(depth0,helpers,partials,data) {
  var stack1, helper, lambda=this.lambda, escapeExpression=this.escapeExpression, functionType="function", helperMissing=helpers.helperMissing;
  return "<table class=\"table-condensed\">\n  <tbody>\n    <tr>\n      <td class=\"ds-tooltip-label\">\n        <span class=\"badge\" style=\"background-color: "
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.series : depth0)) != null ? stack1.color : stack1), depth0))
    + "\"><i></i></span>\n        "
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.series : depth0)) != null ? stack1.label : stack1), depth0))
    + "\n      </td>\n      <td class=\"ds-tooltip-value\">\n        "
    + escapeExpression(((helper = (helper = helpers.value || (depth0 != null ? depth0.value : depth0)) != null ? helper : helperMissing),(typeof helper === functionType ? helper.call(depth0, {"name":"value","hash":{},"data":data}) : helper)))
    + "\n      </td>\n    </tr>\n  </tbody>\n</table>\n";
},"useData":true});

this["ds"]["templates"]["flot"]["donut_tooltip"] = Handlebars.template({"compiler":[6,">= 2.0.0-beta.1"],"main":function(depth0,helpers,partials,data) {
  var stack1, helper, lambda=this.lambda, escapeExpression=this.escapeExpression, functionType="function", helperMissing=helpers.helperMissing;
  return "<table class=\"table-condensed\">\n  <tbody>\n    <tr>\n      <td class=\"ds-tooltip-label\">\n        <span class=\"badge\" style=\"background-color: "
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.series : depth0)) != null ? stack1.color : stack1), depth0))
    + "\"><i></i></span>\n        "
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.series : depth0)) != null ? stack1.label : stack1), depth0))
    + "\n      </td>\n      <td class=\"ds-tooltip-value\">\n        "
    + escapeExpression(((helper = (helper = helpers.value || (depth0 != null ? depth0.value : depth0)) != null ? helper : helperMissing),(typeof helper === functionType ? helper.call(depth0, {"name":"value","hash":{},"data":data}) : helper)))
    + " / "
    + escapeExpression(((helper = (helper = helpers.percent || (depth0 != null ? depth0.percent : depth0)) != null ? helper : helperMissing),(typeof helper === functionType ? helper.call(depth0, {"name":"percent","hash":{},"data":data}) : helper)))
    + "\n      </td>\n    </tr>\n  </tbody>\n</table>\n";
},"useData":true});

this["ds"]["templates"]["flot"]["tooltip"] = Handlebars.template({"1":function(depth0,helpers,partials,data) {
  var stack1, helper, lambda=this.lambda, escapeExpression=this.escapeExpression, functionType="function", helperMissing=helpers.helperMissing;
  return "      <tr>\n        <td class=\"ds-tooltip-label\">\n          <span class=\"badge\" style=\"background-color: "
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.series : depth0)) != null ? stack1.color : stack1), depth0))
    + "\"><i></i></span>\n          "
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.series : depth0)) != null ? stack1.label : stack1), depth0))
    + "\n        </td>\n        <td class=\"ds-tooltip-value\">\n          "
    + escapeExpression(((helper = (helper = helpers.value || (depth0 != null ? depth0.value : depth0)) != null ? helper : helperMissing),(typeof helper === functionType ? helper.call(depth0, {"name":"value","hash":{},"data":data}) : helper)))
    + "\n        </td>\n      </tr>\n";
},"compiler":[6,">= 2.0.0-beta.1"],"main":function(depth0,helpers,partials,data) {
  var stack1, helperMissing=helpers.helperMissing, escapeExpression=this.escapeExpression, buffer = "<table class=\"table-condensed\">\n  <tbody>\n    <tr>\n      <td>\n        <span class=\"ds-tooltip-time\">"
    + escapeExpression(((helpers.moment || (depth0 && depth0.moment) || helperMissing).call(depth0, "dd, M-D-YYYY, h:mm A", (depth0 != null ? depth0.time : depth0), {"name":"moment","hash":{},"data":data})))
    + "</span>\n      </td>\n    </tr>\n";
  stack1 = helpers.each.call(depth0, (depth0 != null ? depth0.items : depth0), {"name":"each","hash":{},"fn":this.program(1, data),"inverse":this.noop,"data":data});
  if (stack1 != null) { buffer += stack1; }
  return buffer + "  </tbody>\n</table>\n";
},"useData":true});

this["ds"]["templates"]["listing"]["dashboard_list"] = Handlebars.template({"1":function(depth0,helpers,partials,data) {
  var stack1, buffer = "";
  stack1 = this.invokePartial(partials['ds-dashboard-listing-entry'], '      ', 'ds-dashboard-listing-entry', depth0, undefined, helpers, partials, data);
  if (stack1 != null) { buffer += stack1; }
  return buffer;
},"3":function(depth0,helpers,partials,data) {
  return "      <tr><td><h3>No dashboards defined</h3></td></tr>\n";
  },"compiler":[6,">= 2.0.0-beta.1"],"main":function(depth0,helpers,partials,data) {
  var stack1, buffer = "<table class=\"table table-hover table-condensed\">\n  <tbody>\n";
  stack1 = helpers.each.call(depth0, (depth0 != null ? depth0.dashboards : depth0), {"name":"each","hash":{},"fn":this.program(1, data),"inverse":this.program(3, data),"data":data});
  if (stack1 != null) { buffer += stack1; }
  return buffer + "  </tbody>\n</table>\n";
},"usePartial":true,"useData":true});

this["ds"]["templates"]["listing"]["dashboard_tag_list"] = Handlebars.template({"1":function(depth0,helpers,partials,data) {
  return "active";
  },"3":function(depth0,helpers,partials,data) {
  var helper, functionType="function", helperMissing=helpers.helperMissing, escapeExpression=this.escapeExpression;
  return "  <li data-ds-tag=\""
    + escapeExpression(((helper = (helper = helpers.name || (depth0 != null ? depth0.name : depth0)) != null ? helper : helperMissing),(typeof helper === functionType ? helper.call(depth0, {"name":"name","hash":{},"data":data}) : helper)))
    + "\">\n    <a href=\"/dashboards/tagged/"
    + escapeExpression(((helper = (helper = helpers.name || (depth0 != null ? depth0.name : depth0)) != null ? helper : helperMissing),(typeof helper === functionType ? helper.call(depth0, {"name":"name","hash":{},"data":data}) : helper)))
    + "\">\n      "
    + escapeExpression(((helper = (helper = helpers.name || (depth0 != null ? depth0.name : depth0)) != null ? helper : helperMissing),(typeof helper === functionType ? helper.call(depth0, {"name":"name","hash":{},"data":data}) : helper)))
    + "\n      <span class=\"badge badge-primary pull-right\">"
    + escapeExpression(((helper = (helper = helpers.count || (depth0 != null ? depth0.count : depth0)) != null ? helper : helperMissing),(typeof helper === functionType ? helper.call(depth0, {"name":"count","hash":{},"data":data}) : helper)))
    + "</span>\n    </a>\n  </li>\n";
},"compiler":[6,">= 2.0.0-beta.1"],"main":function(depth0,helpers,partials,data) {
  var stack1, buffer = "<ul class=\"nav nav-pills nav-stacked\">\n  <li class=\"";
  stack1 = helpers.unless.call(depth0, (depth0 != null ? depth0.tag : depth0), {"name":"unless","hash":{},"fn":this.program(1, data),"inverse":this.noop,"data":data});
  if (stack1 != null) { buffer += stack1; }
  buffer += "\">\n    <a href=\"/dashboards\">\n      All <span class=\"badge badge-primary pull-right\"></span>\n    </a>\n  </li>\n\n";
  stack1 = helpers.each.call(depth0, (depth0 != null ? depth0.tags : depth0), {"name":"each","hash":{},"fn":this.program(3, data),"inverse":this.noop,"data":data});
  if (stack1 != null) { buffer += stack1; }
  return buffer + "</ul>\n";
},"useData":true});

this["ds"]["templates"]["models"]["bar_chart"] = Handlebars.template({"compiler":[6,">= 2.0.0-beta.1"],"main":function(depth0,helpers,partials,data) {
  var stack1, helperMissing=helpers.helperMissing, escapeExpression=this.escapeExpression, lambda=this.lambda, buffer = "<div class=\"ds-item ds-graph ds-bar-chart "
    + escapeExpression(((helpers.css_class || (depth0 && depth0.css_class) || helperMissing).call(depth0, (depth0 != null ? depth0.item : depth0), {"name":"css_class","hash":{},"data":data})))
    + "\"\n  id=\""
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.item_id : stack1), depth0))
    + "\">\n";
  stack1 = this.invokePartial(partials['ds-title-bar'], '  ', 'ds-title-bar', depth0, undefined, helpers, partials, data);
  if (stack1 != null) { buffer += stack1; }
  return buffer + "  <div class=\"ds-graph-holder "
    + escapeExpression(((helpers.height || (depth0 && depth0.height) || helperMissing).call(depth0, (depth0 != null ? depth0.item : depth0), {"name":"height","hash":{},"data":data})))
    + "\">\n    <svg class=\""
    + escapeExpression(((helpers.height || (depth0 && depth0.height) || helperMissing).call(depth0, (depth0 != null ? depth0.item : depth0), {"name":"height","hash":{},"data":data})))
    + "\"></svg>\n  </div>\n  <div class=\"ds-legend-holder\" id=\"ds-legend-"
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.item_id : stack1), depth0))
    + "\">\n  </div>\n</div>\n";
},"usePartial":true,"useData":true});

this["ds"]["templates"]["models"]["cell"] = Handlebars.template({"1":function(depth0,helpers,partials,data) {
  var stack1, lambda=this.lambda, escapeExpression=this.escapeExpression;
  return " align=\""
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.align : stack1), depth0))
    + "\" ";
},"3":function(depth0,helpers,partials,data) {
  var helperMissing=helpers.helperMissing, escapeExpression=this.escapeExpression;
  return "<div class=\""
    + escapeExpression(((helpers.style_class || (depth0 && depth0.style_class) || helperMissing).call(depth0, (depth0 != null ? depth0.item : depth0), {"name":"style_class","hash":{},"data":data})))
    + "\">";
},"5":function(depth0,helpers,partials,data) {
  var helperMissing=helpers.helperMissing, escapeExpression=this.escapeExpression;
  return "    "
    + escapeExpression(((helpers.item || (depth0 && depth0.item) || helperMissing).call(depth0, depth0, {"name":"item","hash":{},"data":data})))
    + "\n";
},"7":function(depth0,helpers,partials,data) {
  return "</div>";
  },"compiler":[6,">= 2.0.0-beta.1"],"main":function(depth0,helpers,partials,data) {
  var stack1, helperMissing=helpers.helperMissing, escapeExpression=this.escapeExpression, lambda=this.lambda, buffer = "<div class=\"ds-cell "
    + escapeExpression(((helpers.span || (depth0 && depth0.span) || helperMissing).call(depth0, (depth0 != null ? depth0.item : depth0), {"name":"span","hash":{},"data":data})))
    + " "
    + escapeExpression(((helpers.offset || (depth0 && depth0.offset) || helperMissing).call(depth0, (depth0 != null ? depth0.item : depth0), {"name":"offset","hash":{},"data":data})))
    + " "
    + escapeExpression(((helpers.css_class || (depth0 && depth0.css_class) || helperMissing).call(depth0, (depth0 != null ? depth0.item : depth0), {"name":"css_class","hash":{},"data":data})))
    + " "
    + escapeExpression(((helpers.height || (depth0 && depth0.height) || helperMissing).call(depth0, (depth0 != null ? depth0.item : depth0), {"name":"height","hash":{},"data":data})))
    + "\"\n     ";
  stack1 = helpers['if'].call(depth0, ((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.align : stack1), {"name":"if","hash":{},"fn":this.program(1, data),"inverse":this.noop,"data":data});
  if (stack1 != null) { buffer += stack1; }
  buffer += " id=\""
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.item_id : stack1), depth0))
    + "\"\n       >\n";
  stack1 = this.invokePartial(partials['ds-edit-bar'], '       ', 'ds-edit-bar', depth0, undefined, helpers, partials, data);
  if (stack1 != null) { buffer += stack1; }
  buffer += "  ";
  stack1 = helpers['if'].call(depth0, ((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.style : stack1), {"name":"if","hash":{},"fn":this.program(3, data),"inverse":this.noop,"data":data});
  if (stack1 != null) { buffer += stack1; }
  buffer += "\n\n";
  stack1 = helpers.each.call(depth0, ((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.items : stack1), {"name":"each","hash":{},"fn":this.program(5, data),"inverse":this.noop,"data":data});
  if (stack1 != null) { buffer += stack1; }
  buffer += "\n    ";
  stack1 = helpers['if'].call(depth0, ((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.style : stack1), {"name":"if","hash":{},"fn":this.program(7, data),"inverse":this.noop,"data":data});
  if (stack1 != null) { buffer += stack1; }
  return buffer + "\n      <i data-ds-show=\"\"\n        style=\"display:none\"\n        title=\"Drag to resize\"\n        class=\"fa fa-arrows-alt pull-right ds-resize-handle\"\n        data-ds-item-id=\""
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.item_id : stack1), depth0))
    + "\"></i>\n</div>\n";
},"usePartial":true,"useData":true});

this["ds"]["templates"]["models"]["comparison_summation_table"] = Handlebars.template({"1":function(depth0,helpers,partials,data) {
  return "table-striped";
  },"3":function(depth0,helpers,partials,data) {
  var stack1, lambda=this.lambda, escapeExpression=this.escapeExpression;
  return escapeExpression(lambda(((stack1 = ((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.query_other : stack1)) != null ? stack1.name : stack1), depth0));
  },"5":function(depth0,helpers,partials,data) {
  var stack1, lambda=this.lambda, escapeExpression=this.escapeExpression;
  return escapeExpression(lambda(((stack1 = ((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.query : stack1)) != null ? stack1.name : stack1), depth0));
  },"compiler":[6,">= 2.0.0-beta.1"],"main":function(depth0,helpers,partials,data) {
  var stack1, lambda=this.lambda, escapeExpression=this.escapeExpression, helperMissing=helpers.helperMissing, buffer = "<div class=\"ds-item\" id=\""
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.item_id : stack1), depth0))
    + "\">\n";
  stack1 = this.invokePartial(partials['ds-title-bar'], '  ', 'ds-title-bar', depth0, undefined, helpers, partials, data);
  if (stack1 != null) { buffer += stack1; }
  buffer += "  <table class=\"table table-condensed ds-timeshift-summation-table "
    + escapeExpression(((helpers.height || (depth0 && depth0.height) || helperMissing).call(depth0, (depth0 != null ? depth0.item : depth0), {"name":"height","hash":{},"data":data})))
    + " "
    + escapeExpression(((helpers.css_class || (depth0 && depth0.css_class) || helperMissing).call(depth0, (depth0 != null ? depth0.item : depth0), {"name":"css_class","hash":{},"data":data})))
    + "\n                ";
  stack1 = helpers['if'].call(depth0, ((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.striped : stack1), {"name":"if","hash":{},"fn":this.program(1, data),"inverse":this.noop,"data":data});
  if (stack1 != null) { buffer += stack1; }
  buffer += "\">\n    <thead>\n      <tr>\n        <th>&nbsp;</th>\n        <th>";
  stack1 = helpers['if'].call(depth0, ((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.query_other : stack1), {"name":"if","hash":{},"fn":this.program(3, data),"inverse":this.noop,"data":data});
  if (stack1 != null) { buffer += stack1; }
  buffer += "</th>\n        <th>";
  stack1 = helpers['if'].call(depth0, ((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.query : stack1), {"name":"if","hash":{},"fn":this.program(5, data),"inverse":this.noop,"data":data});
  if (stack1 != null) { buffer += stack1; }
  return buffer + "</th>\n        <th>Delta</th>\n        <th>%</th>\n      </tr>\n    </thead>\n    <tbody/>\n  </table>\n</div>\n";
},"usePartial":true,"useData":true});

this["ds"]["templates"]["models"]["comparison_summation_table_body"] = Handlebars.template({"compiler":[6,">= 2.0.0-beta.1"],"main":function(depth0,helpers,partials,data) {
  var stack1, helperMissing=helpers.helperMissing, escapeExpression=this.escapeExpression, lambda=this.lambda;
  return "<!-- TODO: configure which rows to include. Sum doesnt make sense for rates -->\n<tr>\n  <th>Average</th>\n    <td>"
    + escapeExpression(((helpers.format || (depth0 && depth0.format) || helperMissing).call(depth0, ((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.format : stack1), ((stack1 = (depth0 != null ? depth0.then : depth0)) != null ? stack1.mean : stack1), {"name":"format","hash":{},"data":data})))
    + "</td>\n  <td>"
    + escapeExpression(((helpers.format || (depth0 && depth0.format) || helperMissing).call(depth0, ((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.format : stack1), ((stack1 = (depth0 != null ? depth0.now : depth0)) != null ? stack1.mean : stack1), {"name":"format","hash":{},"data":data})))
    + "</td>\n  <td class=\""
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.diff : depth0)) != null ? stack1.mean_class : stack1), depth0))
    + "\">\n    "
    + escapeExpression(((helpers.format || (depth0 && depth0.format) || helperMissing).call(depth0, ((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.format : stack1), ((stack1 = (depth0 != null ? depth0.diff : depth0)) != null ? stack1.mean : stack1), {"name":"format","hash":{},"data":data})))
    + "\n  </td>\n  <td class=\""
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.diff : depth0)) != null ? stack1.mean_class : stack1), depth0))
    + "\">\n    "
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.diff : depth0)) != null ? stack1.mean_pct : stack1), depth0))
    + "\n  </td>\n</tr>\n<tr>\n  <th>Min</th>\n  <td>"
    + escapeExpression(((helpers.format || (depth0 && depth0.format) || helperMissing).call(depth0, ((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.format : stack1), ((stack1 = (depth0 != null ? depth0.then : depth0)) != null ? stack1.min : stack1), {"name":"format","hash":{},"data":data})))
    + "</td>\n  <td>"
    + escapeExpression(((helpers.format || (depth0 && depth0.format) || helperMissing).call(depth0, ((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.format : stack1), ((stack1 = (depth0 != null ? depth0.now : depth0)) != null ? stack1.min : stack1), {"name":"format","hash":{},"data":data})))
    + "</td>\n  <td class=\""
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.diff : depth0)) != null ? stack1.min_class : stack1), depth0))
    + "\">\n    "
    + escapeExpression(((helpers.format || (depth0 && depth0.format) || helperMissing).call(depth0, ((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.format : stack1), ((stack1 = (depth0 != null ? depth0.diff : depth0)) != null ? stack1.min : stack1), {"name":"format","hash":{},"data":data})))
    + "\n  </td>\n  <td class=\""
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.diff : depth0)) != null ? stack1.min_class : stack1), depth0))
    + "\">\n    "
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.diff : depth0)) != null ? stack1.min_pct : stack1), depth0))
    + "\n  </td>\n</tr>\n<tr>\n  <th>Max</th>\n  <td>"
    + escapeExpression(((helpers.format || (depth0 && depth0.format) || helperMissing).call(depth0, ((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.format : stack1), ((stack1 = (depth0 != null ? depth0.then : depth0)) != null ? stack1.max : stack1), {"name":"format","hash":{},"data":data})))
    + "</td>\n  <td>"
    + escapeExpression(((helpers.format || (depth0 && depth0.format) || helperMissing).call(depth0, ((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.format : stack1), ((stack1 = (depth0 != null ? depth0.now : depth0)) != null ? stack1.max : stack1), {"name":"format","hash":{},"data":data})))
    + "</td>\n  <td class=\""
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.diff : depth0)) != null ? stack1.max_class : stack1), depth0))
    + "\">\n    "
    + escapeExpression(((helpers.format || (depth0 && depth0.format) || helperMissing).call(depth0, ((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.format : stack1), ((stack1 = (depth0 != null ? depth0.diff : depth0)) != null ? stack1.max : stack1), {"name":"format","hash":{},"data":data})))
    + "\n  </td>\n  <td class=\""
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.diff : depth0)) != null ? stack1.max_class : stack1), depth0))
    + "\">\n    "
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.diff : depth0)) != null ? stack1.max_pct : stack1), depth0))
    + "\n  </td>\n</tr>\n<tr>\n  <th>Sum</th>\n  <td>"
    + escapeExpression(((helpers.format || (depth0 && depth0.format) || helperMissing).call(depth0, ((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.format : stack1), ((stack1 = (depth0 != null ? depth0.then : depth0)) != null ? stack1.sum : stack1), {"name":"format","hash":{},"data":data})))
    + "</td>\n  <td>"
    + escapeExpression(((helpers.format || (depth0 && depth0.format) || helperMissing).call(depth0, ((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.format : stack1), ((stack1 = (depth0 != null ? depth0.now : depth0)) != null ? stack1.sum : stack1), {"name":"format","hash":{},"data":data})))
    + "</td>\n  <td class=\""
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.diff : depth0)) != null ? stack1.sum_class : stack1), depth0))
    + "\">\n    "
    + escapeExpression(((helpers.format || (depth0 && depth0.format) || helperMissing).call(depth0, ((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.format : stack1), ((stack1 = (depth0 != null ? depth0.diff : depth0)) != null ? stack1.sum : stack1), {"name":"format","hash":{},"data":data})))
    + "\n  </td>\n  <td class=\""
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.diff : depth0)) != null ? stack1.sum_class : stack1), depth0))
    + "\">\n    "
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.diff : depth0)) != null ? stack1.sum_pct : stack1), depth0))
    + "\n  </td>\n</tr>\n";
},"useData":true});

this["ds"]["templates"]["models"]["definition"] = Handlebars.template({"1":function(depth0,helpers,partials,data) {
  var helperMissing=helpers.helperMissing, escapeExpression=this.escapeExpression;
  return "    "
    + escapeExpression(((helpers.item || (depth0 && depth0.item) || helperMissing).call(depth0, depth0, {"name":"item","hash":{},"data":data})))
    + "\n";
},"compiler":[6,">= 2.0.0-beta.1"],"main":function(depth0,helpers,partials,data) {
  var stack1, helperMissing=helpers.helperMissing, escapeExpression=this.escapeExpression, lambda=this.lambda, buffer = "<div class=\""
    + escapeExpression(((helpers.css_class || (depth0 && depth0.css_class) || helperMissing).call(depth0, (depth0 != null ? depth0.item : depth0), {"name":"css_class","hash":{},"data":data})))
    + " ds-dashboard\" id=\""
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.item_id : stack1), depth0))
    + "\">\n";
  stack1 = helpers.each.call(depth0, ((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.items : stack1), {"name":"each","hash":{},"fn":this.program(1, data),"inverse":this.noop,"data":data});
  if (stack1 != null) { buffer += stack1; }
  return buffer + "</div>\n";
},"useData":true});

this["ds"]["templates"]["models"]["discrete_bar_chart"] = Handlebars.template({"compiler":[6,">= 2.0.0-beta.1"],"main":function(depth0,helpers,partials,data) {
  var stack1, helperMissing=helpers.helperMissing, escapeExpression=this.escapeExpression, lambda=this.lambda, buffer = "<div class=\"ds-item ds-graph ds-discrete-bar-chart "
    + escapeExpression(((helpers.css_class || (depth0 && depth0.css_class) || helperMissing).call(depth0, (depth0 != null ? depth0.item : depth0), {"name":"css_class","hash":{},"data":data})))
    + "\"\n  id=\""
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.item_id : stack1), depth0))
    + "\">\n";
  stack1 = this.invokePartial(partials['ds-title-bar'], '  ', 'ds-title-bar', depth0, undefined, helpers, partials, data);
  if (stack1 != null) { buffer += stack1; }
  return buffer + "  <div class=\"ds-graph-holder "
    + escapeExpression(((helpers.height || (depth0 && depth0.height) || helperMissing).call(depth0, (depth0 != null ? depth0.item : depth0), {"name":"height","hash":{},"data":data})))
    + "\">\n    <svg class=\""
    + escapeExpression(((helpers.height || (depth0 && depth0.height) || helperMissing).call(depth0, (depth0 != null ? depth0.item : depth0), {"name":"height","hash":{},"data":data})))
    + "\"></svg>\n  </div>\n  <div class=\"ds-legend-holder\" id=\"ds-legend-"
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.item_id : stack1), depth0))
    + "\">\n  </div>\n</div>\n";
},"usePartial":true,"useData":true});

this["ds"]["templates"]["models"]["donut_chart"] = Handlebars.template({"compiler":[6,">= 2.0.0-beta.1"],"main":function(depth0,helpers,partials,data) {
  var stack1, helperMissing=helpers.helperMissing, escapeExpression=this.escapeExpression, lambda=this.lambda, buffer = "<div class=\"ds-item ds-graph ds-donut-chart "
    + escapeExpression(((helpers.css_class || (depth0 && depth0.css_class) || helperMissing).call(depth0, (depth0 != null ? depth0.item : depth0), {"name":"css_class","hash":{},"data":data})))
    + "\"\n  id=\""
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.item_id : stack1), depth0))
    + "\">\n";
  stack1 = this.invokePartial(partials['ds-title-bar'], '  ', 'ds-title-bar', depth0, undefined, helpers, partials, data);
  if (stack1 != null) { buffer += stack1; }
  return buffer + "  <div class=\"ds-graph-holder "
    + escapeExpression(((helpers.height || (depth0 && depth0.height) || helperMissing).call(depth0, (depth0 != null ? depth0.item : depth0), {"name":"height","hash":{},"data":data})))
    + "\">\n    <svg class=\""
    + escapeExpression(((helpers.height || (depth0 && depth0.height) || helperMissing).call(depth0, (depth0 != null ? depth0.item : depth0), {"name":"height","hash":{},"data":data})))
    + "\"></svg>\n  </div>\n  <div class=\"ds-legend-holder\" id=\"ds-legend-"
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.item_id : stack1), depth0))
    + "\">\n  </div>\n</div>\n";
},"usePartial":true,"useData":true});

this["ds"]["templates"]["models"]["heading"] = Handlebars.template({"1":function(depth0,helpers,partials,data) {
  var stack1, lambda=this.lambda, escapeExpression=this.escapeExpression;
  return "class=\""
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.css_class : stack1), depth0))
    + "\"";
},"3":function(depth0,helpers,partials,data) {
  var stack1, lambda=this.lambda, escapeExpression=this.escapeExpression;
  return "<small>"
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.description : stack1), depth0))
    + "</small>";
},"compiler":[6,">= 2.0.0-beta.1"],"main":function(depth0,helpers,partials,data) {
  var stack1, lambda=this.lambda, escapeExpression=this.escapeExpression, helperMissing=helpers.helperMissing, buffer = "<div class=\"ds-item ds-heading\" id=\""
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.item_id : stack1), depth0))
    + "\">\n  "
    + escapeExpression(((helpers['ds-edit-bar'] || (depth0 && depth0['ds-edit-bar']) || helperMissing).call(depth0, (depth0 != null ? depth0.item : depth0), {"name":"ds-edit-bar","hash":{},"data":data})))
    + "\n  <h"
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.level : stack1), depth0))
    + " ";
  stack1 = helpers['if'].call(depth0, ((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.css_class : stack1), {"name":"if","hash":{},"fn":this.program(1, data),"inverse":this.noop,"data":data});
  if (stack1 != null) { buffer += stack1; }
  buffer += ">\n    "
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.text : stack1), depth0))
    + " ";
  stack1 = helpers['if'].call(depth0, ((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.description : stack1), {"name":"if","hash":{},"fn":this.program(3, data),"inverse":this.noop,"data":data});
  if (stack1 != null) { buffer += stack1; }
  return buffer + "\n      </h"
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.level : stack1), depth0))
    + ">\n</div>\n";
},"useData":true});

this["ds"]["templates"]["models"]["jumbotron_singlestat"] = Handlebars.template({"compiler":[6,">= 2.0.0-beta.1"],"main":function(depth0,helpers,partials,data) {
  var stack1, lambda=this.lambda, escapeExpression=this.escapeExpression, helperMissing=helpers.helperMissing;
  return "<div class=\"ds-item ds-jumbotron-singlestat\" id=\""
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.item_id : stack1), depth0))
    + "\">\n  "
    + escapeExpression(((helpers['ds-edit-bar'] || (depth0 && depth0['ds-edit-bar']) || helperMissing).call(depth0, (depth0 != null ? depth0.item : depth0), {"name":"ds-edit-bar","hash":{},"data":data})))
    + "\n  <div class=\""
    + escapeExpression(((helpers.height || (depth0 && depth0.height) || helperMissing).call(depth0, (depth0 != null ? depth0.item : depth0), {"name":"height","hash":{},"data":data})))
    + " "
    + escapeExpression(((helpers.css_class || (depth0 && depth0.css_class) || helperMissing).call(depth0, (depth0 != null ? depth0.item : depth0), {"name":"css_class","hash":{},"data":data})))
    + "\"\n    >\n    <div><p><span class=\"value\"></span><span class=\"unit\">"
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.units : stack1), depth0))
    + "</span></p></div>\n    <div><h3>"
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.title : stack1), depth0))
    + "</h3></div>\n  </div>\n</div>\n";
},"useData":true});

this["ds"]["templates"]["models"]["markdown"] = Handlebars.template({"1":function(depth0,helpers,partials,data) {
  var stack1, lambda=this.lambda, escapeExpression=this.escapeExpression;
  return "    <pre>"
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.text : stack1), depth0))
    + "</pre>\n";
},"3":function(depth0,helpers,partials,data) {
  var stack1, buffer = "   ";
  stack1 = helpers['if'].call(depth0, ((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.expanded_text : stack1), {"name":"if","hash":{},"fn":this.program(4, data),"inverse":this.program(6, data),"data":data});
  if (stack1 != null) { buffer += stack1; }
  return buffer + "\n";
},"4":function(depth0,helpers,partials,data) {
  var stack1, helperMissing=helpers.helperMissing, escapeExpression=this.escapeExpression;
  return escapeExpression(((helpers.markdown || (depth0 && depth0.markdown) || helperMissing).call(depth0, ((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.expanded_text : stack1), {"name":"markdown","hash":{},"data":data})));
  },"6":function(depth0,helpers,partials,data) {
  var stack1, helperMissing=helpers.helperMissing, escapeExpression=this.escapeExpression;
  return escapeExpression(((helpers.markdown || (depth0 && depth0.markdown) || helperMissing).call(depth0, ((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.text : stack1), {"name":"markdown","hash":{},"data":data})));
  },"compiler":[6,">= 2.0.0-beta.1"],"main":function(depth0,helpers,partials,data) {
  var stack1, helperMissing=helpers.helperMissing, escapeExpression=this.escapeExpression, lambda=this.lambda, buffer = "<div class=\"ds-item ds-markdown "
    + escapeExpression(((helpers.height || (depth0 && depth0.height) || helperMissing).call(depth0, (depth0 != null ? depth0.item : depth0), {"name":"height","hash":{},"data":data})))
    + " "
    + escapeExpression(((helpers.css_class || (depth0 && depth0.css_class) || helperMissing).call(depth0, (depth0 != null ? depth0.item : depth0), {"name":"css_class","hash":{},"data":data})))
    + "\" id=\""
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.item_id : stack1), depth0))
    + "\">\n  "
    + escapeExpression(((helpers['ds-edit-bar'] || (depth0 && depth0['ds-edit-bar']) || helperMissing).call(depth0, (depth0 != null ? depth0.item : depth0), {"name":"ds-edit-bar","hash":{},"data":data})))
    + "\n";
  stack1 = helpers['if'].call(depth0, ((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.raw : stack1), {"name":"if","hash":{},"fn":this.program(1, data),"inverse":this.program(3, data),"data":data});
  if (stack1 != null) { buffer += stack1; }
  return buffer + "</div>\n";
},"useData":true});

this["ds"]["templates"]["models"]["percentage_table"] = Handlebars.template({"compiler":[6,">= 2.0.0-beta.1"],"main":function(depth0,helpers,partials,data) {
  var stack1, lambda=this.lambda, escapeExpression=this.escapeExpression, buffer = "<div class=\"ds-item\" id=\""
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.item_id : stack1), depth0))
    + "\">\n";
  stack1 = this.invokePartial(partials['ds-title-bar'], '  ', 'ds-title-bar', depth0, undefined, helpers, partials, data);
  if (stack1 != null) { buffer += stack1; }
  return buffer + "  <div class=\"ds-percentage-table-holder\">\n    <h4>No data</h4>\n  </div>\n</div>\n";
},"usePartial":true,"useData":true});

this["ds"]["templates"]["models"]["percentage_table_data"] = Handlebars.template({"1":function(depth0,helpers,partials,data) {
  return "table-striped";
  },"3":function(depth0,helpers,partials,data,depths) {
  var stack1, buffer = "    <thead>\n      <tr>\n        <th>&nbsp;</th>\n        <th>%</th>\n";
  stack1 = helpers['if'].call(depth0, ((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.include_sums : stack1), {"name":"if","hash":{},"fn":this.program(4, data, depths),"inverse":this.noop,"data":data});
  if (stack1 != null) { buffer += stack1; }
  buffer += "      </tr>\n    </thead>\n\n    <tbody>\n";
  stack1 = helpers.each.call(depth0, ((stack1 = (depth0 != null ? depth0.query : depth0)) != null ? stack1.data : stack1), {"name":"each","hash":{},"fn":this.program(6, data, depths),"inverse":this.noop,"data":data});
  if (stack1 != null) { buffer += stack1; }
  buffer += "\n";
  stack1 = helpers['if'].call(depth0, ((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.include_sums : stack1), {"name":"if","hash":{},"fn":this.program(9, data, depths),"inverse":this.noop,"data":data});
  if (stack1 != null) { buffer += stack1; }
  return buffer + "    </tbody>\n";
},"4":function(depth0,helpers,partials,data) {
  var stack1, lambda=this.lambda, escapeExpression=this.escapeExpression;
  return "          <th>"
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.transform : stack1), depth0))
    + "</th>\n";
},"6":function(depth0,helpers,partials,data,depths) {
  var stack1, helper, functionType="function", helperMissing=helpers.helperMissing, escapeExpression=this.escapeExpression, buffer = "        <tr>\n          <th>"
    + escapeExpression(((helper = (helper = helpers.target || (depth0 != null ? depth0.target : depth0)) != null ? helper : helperMissing),(typeof helper === functionType ? helper.call(depth0, {"name":"target","hash":{},"data":data}) : helper)))
    + "</th>\n          <td>"
    + escapeExpression(((helpers.format || (depth0 && depth0.format) || helperMissing).call(depth0, ",.2%", ((stack1 = (depth0 != null ? depth0.summation : depth0)) != null ? stack1.percent : stack1), {"name":"format","hash":{},"data":data})))
    + "</td>\n";
  stack1 = helpers['if'].call(depth0, ((stack1 = (depths[1] != null ? depths[1].item : depths[1])) != null ? stack1.include_sums : stack1), {"name":"if","hash":{},"fn":this.program(7, data, depths),"inverse":this.noop,"data":data});
  if (stack1 != null) { buffer += stack1; }
  return buffer + "        </tr>\n";
},"7":function(depth0,helpers,partials,data) {
  var stack1, helperMissing=helpers.helperMissing, escapeExpression=this.escapeExpression;
  return "            <td>"
    + escapeExpression(((helpers.format || (depth0 && depth0.format) || helperMissing).call(depth0, ",.0f", ((stack1 = (depth0 != null ? depth0.summation : depth0)) != null ? stack1.percent_value : stack1), {"name":"format","hash":{},"data":data})))
    + "</td>\n";
},"9":function(depth0,helpers,partials,data) {
  var stack1, helperMissing=helpers.helperMissing, escapeExpression=this.escapeExpression;
  return "        <tr>\n          <th>Total</th>\n          <td></td>\n          <td>"
    + escapeExpression(((helpers.format || (depth0 && depth0.format) || helperMissing).call(depth0, ",.0f", ((stack1 = ((stack1 = (depth0 != null ? depth0.query : depth0)) != null ? stack1.summation : stack1)) != null ? stack1.percent_value : stack1), {"name":"format","hash":{},"data":data})))
    + "</td>\n        </tr>\n";
},"11":function(depth0,helpers,partials,data,depths) {
  var stack1, buffer = "    <thead>\n      <tr>\n";
  stack1 = helpers['if'].call(depth0, ((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.include_sums : stack1), {"name":"if","hash":{},"fn":this.program(12, data, depths),"inverse":this.noop,"data":data});
  if (stack1 != null) { buffer += stack1; }
  stack1 = helpers.each.call(depth0, ((stack1 = (depth0 != null ? depth0.query : depth0)) != null ? stack1.data : stack1), {"name":"each","hash":{},"fn":this.program(14, data, depths),"inverse":this.noop,"data":data});
  if (stack1 != null) { buffer += stack1; }
  buffer += "      </tr>\n    </thead>\n\n    <tbody>\n      <tr>\n";
  stack1 = helpers['if'].call(depth0, ((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.include_sums : stack1), {"name":"if","hash":{},"fn":this.program(16, data, depths),"inverse":this.noop,"data":data});
  if (stack1 != null) { buffer += stack1; }
  stack1 = helpers.each.call(depth0, ((stack1 = (depth0 != null ? depth0.query : depth0)) != null ? stack1.data : stack1), {"name":"each","hash":{},"fn":this.program(18, data, depths),"inverse":this.noop,"data":data});
  if (stack1 != null) { buffer += stack1; }
  buffer += "      </tr>\n\n";
  stack1 = helpers['if'].call(depth0, ((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.include_sums : stack1), {"name":"if","hash":{},"fn":this.program(20, data, depths),"inverse":this.noop,"data":data});
  if (stack1 != null) { buffer += stack1; }
  return buffer + "    </tbody>\n";
},"12":function(depth0,helpers,partials,data) {
  return "          <th>&nbsp;</th>\n          <th>Total</th>\n";
  },"14":function(depth0,helpers,partials,data) {
  var helper, functionType="function", helperMissing=helpers.helperMissing, escapeExpression=this.escapeExpression;
  return "          <th>"
    + escapeExpression(((helper = (helper = helpers.target || (depth0 != null ? depth0.target : depth0)) != null ? helper : helperMissing),(typeof helper === functionType ? helper.call(depth0, {"name":"target","hash":{},"data":data}) : helper)))
    + "</th>\n";
},"16":function(depth0,helpers,partials,data) {
  return "          <th>%</th>\n          <th></th>\n";
  },"18":function(depth0,helpers,partials,data) {
  var stack1, helperMissing=helpers.helperMissing, escapeExpression=this.escapeExpression;
  return "          <td>"
    + escapeExpression(((helpers.format || (depth0 && depth0.format) || helperMissing).call(depth0, ",.2%", ((stack1 = (depth0 != null ? depth0.summation : depth0)) != null ? stack1.percent : stack1), {"name":"format","hash":{},"data":data})))
    + "</td>\n";
},"20":function(depth0,helpers,partials,data,depths) {
  var stack1, lambda=this.lambda, escapeExpression=this.escapeExpression, helperMissing=helpers.helperMissing, buffer = "        <tr>\n          <th>"
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.transform : stack1), depth0))
    + "</th>\n          <td>"
    + escapeExpression(((helpers.format || (depth0 && depth0.format) || helperMissing).call(depth0, ((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.format : stack1), ((stack1 = ((stack1 = (depth0 != null ? depth0.query : depth0)) != null ? stack1.summation : stack1)) != null ? stack1.percent_value : stack1), {"name":"format","hash":{},"data":data})))
    + "</td>\n";
  stack1 = helpers.each.call(depth0, ((stack1 = (depth0 != null ? depth0.query : depth0)) != null ? stack1.data : stack1), {"name":"each","hash":{},"fn":this.program(21, data, depths),"inverse":this.noop,"data":data});
  if (stack1 != null) { buffer += stack1; }
  return buffer + "        </tr>\n";
},"21":function(depth0,helpers,partials,data,depths) {
  var stack1, helperMissing=helpers.helperMissing, escapeExpression=this.escapeExpression;
  return "            <td>"
    + escapeExpression(((helpers.format || (depth0 && depth0.format) || helperMissing).call(depth0, ((stack1 = (depths[2] != null ? depths[2].item : depths[2])) != null ? stack1.format : stack1), ((stack1 = (depth0 != null ? depth0.summation : depth0)) != null ? stack1.percent_value : stack1), {"name":"format","hash":{},"data":data})))
    + "</td>\n";
},"compiler":[6,">= 2.0.0-beta.1"],"main":function(depth0,helpers,partials,data,depths) {
  var stack1, helperMissing=helpers.helperMissing, escapeExpression=this.escapeExpression, buffer = "<table class=\"table table-condensed ds-percentage-table "
    + escapeExpression(((helpers.css_class || (depth0 && depth0.css_class) || helperMissing).call(depth0, (depth0 != null ? depth0.item : depth0), {"name":"css_class","hash":{},"data":data})))
    + "\n                ";
  stack1 = helpers['if'].call(depth0, ((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.striped : stack1), {"name":"if","hash":{},"fn":this.program(1, data, depths),"inverse":this.noop,"data":data});
  if (stack1 != null) { buffer += stack1; }
  buffer += "\">\n\n";
  stack1 = helpers['if'].call(depth0, ((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.invert_axes : stack1), {"name":"if","hash":{},"fn":this.program(3, data, depths),"inverse":this.program(11, data, depths),"data":data});
  if (stack1 != null) { buffer += stack1; }
  return buffer + "\n</table>\n";
},"useData":true,"useDepths":true});

this["ds"]["templates"]["models"]["row"] = Handlebars.template({"1":function(depth0,helpers,partials,data) {
  var helperMissing=helpers.helperMissing, escapeExpression=this.escapeExpression;
  return "<div class=\""
    + escapeExpression(((helpers.style_class || (depth0 && depth0.style_class) || helperMissing).call(depth0, (depth0 != null ? depth0.item : depth0), {"name":"style_class","hash":{},"data":data})))
    + "\">";
},"3":function(depth0,helpers,partials,data) {
  var helperMissing=helpers.helperMissing, escapeExpression=this.escapeExpression;
  return "        "
    + escapeExpression(((helpers.item || (depth0 && depth0.item) || helperMissing).call(depth0, depth0, {"name":"item","hash":{},"data":data})))
    + "\n";
},"5":function(depth0,helpers,partials,data) {
  return "</div>";
  },"compiler":[6,">= 2.0.0-beta.1"],"main":function(depth0,helpers,partials,data) {
  var stack1, lambda=this.lambda, escapeExpression=this.escapeExpression, helperMissing=helpers.helperMissing, buffer = "<div class=\"ds-row\" id=\""
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.item_id : stack1), depth0))
    + "\">\n  ";
  stack1 = helpers['if'].call(depth0, ((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.style : stack1), {"name":"if","hash":{},"fn":this.program(1, data),"inverse":this.noop,"data":data});
  if (stack1 != null) { buffer += stack1; }
  buffer += "\n\n";
  stack1 = this.invokePartial(partials['ds-edit-bar'], '    ', 'ds-edit-bar', depth0, undefined, helpers, partials, data);
  if (stack1 != null) { buffer += stack1; }
  buffer += "    <div class=\"row "
    + escapeExpression(((helpers.css_class || (depth0 && depth0.css_class) || helperMissing).call(depth0, (depth0 != null ? depth0.item : depth0), {"name":"css_class","hash":{},"data":data})))
    + "\">\n";
  stack1 = helpers.each.call(depth0, ((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.items : stack1), {"name":"each","hash":{},"fn":this.program(3, data),"inverse":this.noop,"data":data});
  if (stack1 != null) { buffer += stack1; }
  buffer += "    </div>\n    ";
  stack1 = helpers['if'].call(depth0, ((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.style : stack1), {"name":"if","hash":{},"fn":this.program(5, data),"inverse":this.noop,"data":data});
  if (stack1 != null) { buffer += stack1; }
  return buffer + "\n</div>\n";
},"usePartial":true,"useData":true});

this["ds"]["templates"]["models"]["section"] = Handlebars.template({"1":function(depth0,helpers,partials,data) {
  var helperMissing=helpers.helperMissing, escapeExpression=this.escapeExpression;
  return "<div class=\""
    + escapeExpression(((helpers.style_class || (depth0 && depth0.style_class) || helperMissing).call(depth0, (depth0 != null ? depth0.item : depth0), {"name":"style_class","hash":{},"data":data})))
    + "\">";
},"3":function(depth0,helpers,partials,data) {
  var stack1, lambda=this.lambda, escapeExpression=this.escapeExpression, buffer = "        <h"
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.level : stack1), depth0))
    + " class=\"ds-section-heading\">"
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.title : stack1), depth0))
    + "\n        ";
  stack1 = helpers['if'].call(depth0, ((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.description : stack1), {"name":"if","hash":{},"fn":this.program(4, data),"inverse":this.noop,"data":data});
  if (stack1 != null) { buffer += stack1; }
  return buffer + "\n          </h"
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.level : stack1), depth0))
    + ">\n";
},"4":function(depth0,helpers,partials,data) {
  var stack1, lambda=this.lambda, escapeExpression=this.escapeExpression;
  return "<small>"
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.description : stack1), depth0))
    + "</small>";
},"6":function(depth0,helpers,partials,data) {
  return "        <hr/>\n";
  },"8":function(depth0,helpers,partials,data) {
  var helperMissing=helpers.helperMissing, escapeExpression=this.escapeExpression;
  return "      "
    + escapeExpression(((helpers.item || (depth0 && depth0.item) || helperMissing).call(depth0, depth0, {"name":"item","hash":{},"data":data})))
    + "\n";
},"10":function(depth0,helpers,partials,data) {
  return "</div>";
  },"compiler":[6,">= 2.0.0-beta.1"],"main":function(depth0,helpers,partials,data) {
  var stack1, helperMissing=helpers.helperMissing, escapeExpression=this.escapeExpression, lambda=this.lambda, buffer = "<div class=\"ds-section "
    + escapeExpression(((helpers.container_class || (depth0 && depth0.container_class) || helperMissing).call(depth0, (depth0 != null ? depth0.item : depth0), {"name":"container_class","hash":{},"data":data})))
    + " "
    + escapeExpression(((helpers.css_class || (depth0 && depth0.css_class) || helperMissing).call(depth0, (depth0 != null ? depth0.item : depth0), {"name":"css_class","hash":{},"data":data})))
    + "\" id=\""
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.item_id : stack1), depth0))
    + "\">\n";
  stack1 = this.invokePartial(partials['ds-edit-bar'], '  ', 'ds-edit-bar', depth0, undefined, helpers, partials, data);
  if (stack1 != null) { buffer += stack1; }
  buffer += "  ";
  stack1 = helpers['if'].call(depth0, ((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.style : stack1), {"name":"if","hash":{},"fn":this.program(1, data),"inverse":this.noop,"data":data});
  if (stack1 != null) { buffer += stack1; }
  buffer += "\n    <div>\n";
  stack1 = helpers['if'].call(depth0, ((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.title : stack1), {"name":"if","hash":{},"fn":this.program(3, data),"inverse":this.noop,"data":data});
  if (stack1 != null) { buffer += stack1; }
  stack1 = helpers['if'].call(depth0, ((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.horizontal_rule : stack1), {"name":"if","hash":{},"fn":this.program(6, data),"inverse":this.noop,"data":data});
  if (stack1 != null) { buffer += stack1; }
  buffer += "    </div>\n\n";
  stack1 = helpers.each.call(depth0, ((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.items : stack1), {"name":"each","hash":{},"fn":this.program(8, data),"inverse":this.noop,"data":data});
  if (stack1 != null) { buffer += stack1; }
  buffer += "\n    ";
  stack1 = helpers['if'].call(depth0, ((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.style : stack1), {"name":"if","hash":{},"fn":this.program(10, data),"inverse":this.noop,"data":data});
  if (stack1 != null) { buffer += stack1; }
  return buffer + "\n</div>\n";
},"usePartial":true,"useData":true});

this["ds"]["templates"]["models"]["separator"] = Handlebars.template({"1":function(depth0,helpers,partials,data) {
  var stack1, lambda=this.lambda, escapeExpression=this.escapeExpression;
  return "class=\""
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.css_class : stack1), depth0))
    + "\"";
},"compiler":[6,">= 2.0.0-beta.1"],"main":function(depth0,helpers,partials,data) {
  var stack1, lambda=this.lambda, escapeExpression=this.escapeExpression, helperMissing=helpers.helperMissing, buffer = "<div class=\"ds-item ds-separator\" id=\""
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.item_id : stack1), depth0))
    + "\">\n  "
    + escapeExpression(((helpers['ds-edit-bar'] || (depth0 && depth0['ds-edit-bar']) || helperMissing).call(depth0, (depth0 != null ? depth0.item : depth0), {"name":"ds-edit-bar","hash":{},"data":data})))
    + "\n  <hr ";
  stack1 = helpers['if'].call(depth0, ((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.css_class : stack1), {"name":"if","hash":{},"fn":this.program(1, data),"inverse":this.noop,"data":data});
  if (stack1 != null) { buffer += stack1; }
  return buffer + "></hr>\n</div>\n";
},"useData":true});

this["ds"]["templates"]["models"]["simple_time_series"] = Handlebars.template({"compiler":[6,">= 2.0.0-beta.1"],"main":function(depth0,helpers,partials,data) {
  var stack1, helperMissing=helpers.helperMissing, escapeExpression=this.escapeExpression, lambda=this.lambda, buffer = "<div class=\"ds-item ds-graph ds-simple-time-series "
    + escapeExpression(((helpers.css_class || (depth0 && depth0.css_class) || helperMissing).call(depth0, (depth0 != null ? depth0.item : depth0), {"name":"css_class","hash":{},"data":data})))
    + "\" id=\""
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.item_id : stack1), depth0))
    + "\">\n";
  stack1 = this.invokePartial(partials['ds-title-bar'], '  ', 'ds-title-bar', depth0, undefined, helpers, partials, data);
  if (stack1 != null) { buffer += stack1; }
  return buffer + "  <div class=\"ds-graph-holder "
    + escapeExpression(((helpers.height || (depth0 && depth0.height) || helperMissing).call(depth0, (depth0 != null ? depth0.item : depth0), {"name":"height","hash":{},"data":data})))
    + "\">\n    <svg class=\""
    + escapeExpression(((helpers.height || (depth0 && depth0.height) || helperMissing).call(depth0, (depth0 != null ? depth0.item : depth0), {"name":"height","hash":{},"data":data})))
    + "\"></svg>\n  </div>\n</div>\n";
},"usePartial":true,"useData":true});

this["ds"]["templates"]["models"]["singlegraph"] = Handlebars.template({"compiler":[6,">= 2.0.0-beta.1"],"main":function(depth0,helpers,partials,data) {
  var stack1, helperMissing=helpers.helperMissing, escapeExpression=this.escapeExpression, lambda=this.lambda, buffer = "<div class=\"ds-item ds-graph ds-singlegraph "
    + escapeExpression(((helpers.css_class || (depth0 && depth0.css_class) || helperMissing).call(depth0, (depth0 != null ? depth0.item : depth0), {"name":"css_class","hash":{},"data":data})))
    + "\" id=\""
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.item_id : stack1), depth0))
    + "\">\n";
  stack1 = this.invokePartial(partials['ds-title-bar'], '  ', 'ds-title-bar', depth0, undefined, helpers, partials, data);
  if (stack1 != null) { buffer += stack1; }
  return buffer + "  <span class=\"ds-label\"></span>\n  <span class=\"value\"></span>\n  <div class=\"ds-graph-holder "
    + escapeExpression(((helpers.height || (depth0 && depth0.height) || helperMissing).call(depth0, (depth0 != null ? depth0.item : depth0), {"name":"height","hash":{},"data":data})))
    + "\">\n    <svg class=\""
    + escapeExpression(((helpers.height || (depth0 && depth0.height) || helperMissing).call(depth0, (depth0 != null ? depth0.item : depth0), {"name":"height","hash":{},"data":data})))
    + "\"></svg>\n  </div>\n</div>\n";
},"usePartial":true,"useData":true});

this["ds"]["templates"]["models"]["singlestat"] = Handlebars.template({"compiler":[6,">= 2.0.0-beta.1"],"main":function(depth0,helpers,partials,data) {
  var stack1, lambda=this.lambda, escapeExpression=this.escapeExpression, helperMissing=helpers.helperMissing;
  return "<div class=\"ds-item\" id=\""
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.item_id : stack1), depth0))
    + "\">\n  "
    + escapeExpression(((helpers['ds-edit-bar'] || (depth0 && depth0['ds-edit-bar']) || helperMissing).call(depth0, (depth0 != null ? depth0.item : depth0), {"name":"ds-edit-bar","hash":{},"data":data})))
    + "\n  <div class=\"ds-singlestat "
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.css_class : stack1), depth0))
    + " "
    + escapeExpression(((helpers.height || (depth0 && depth0.height) || helperMissing).call(depth0, (depth0 != null ? depth0.item : depth0), {"name":"height","hash":{},"data":data})))
    + "\">\n    <h3>"
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.title : stack1), depth0))
    + "</h3>\n    <p><span class=\"value\"></span><span class=\"unit\">"
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.units : stack1), depth0))
    + "</span></p>\n  </div>\n</div>\n";
},"useData":true});

this["ds"]["templates"]["models"]["stacked_area_chart"] = Handlebars.template({"compiler":[6,">= 2.0.0-beta.1"],"main":function(depth0,helpers,partials,data) {
  var stack1, helperMissing=helpers.helperMissing, escapeExpression=this.escapeExpression, lambda=this.lambda, buffer = "<div class=\"ds-item ds-graph ds-stacked-area-chart "
    + escapeExpression(((helpers.css_class || (depth0 && depth0.css_class) || helperMissing).call(depth0, (depth0 != null ? depth0.item : depth0), {"name":"css_class","hash":{},"data":data})))
    + "\"\n  id=\""
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.item_id : stack1), depth0))
    + "\">\n";
  stack1 = this.invokePartial(partials['ds-title-bar'], '  ', 'ds-title-bar', depth0, undefined, helpers, partials, data);
  if (stack1 != null) { buffer += stack1; }
  return buffer + "  <div class=\"ds-graph-holder "
    + escapeExpression(((helpers.height || (depth0 && depth0.height) || helperMissing).call(depth0, (depth0 != null ? depth0.item : depth0), {"name":"height","hash":{},"data":data})))
    + "\">\n    <svg class=\""
    + escapeExpression(((helpers.height || (depth0 && depth0.height) || helperMissing).call(depth0, (depth0 != null ? depth0.item : depth0), {"name":"height","hash":{},"data":data})))
    + "\"></svg>\n  </div>\n  <div class=\"ds-legend-holder\" id=\"ds-legend-"
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.item_id : stack1), depth0))
    + "\">\n  </div>\n</div>\n";
},"usePartial":true,"useData":true});

this["ds"]["templates"]["models"]["standard_time_series"] = Handlebars.template({"compiler":[6,">= 2.0.0-beta.1"],"main":function(depth0,helpers,partials,data) {
  var stack1, helperMissing=helpers.helperMissing, escapeExpression=this.escapeExpression, lambda=this.lambda, buffer = "<div class=\"ds-item ds-graph ds-standard-time-series "
    + escapeExpression(((helpers.css_class || (depth0 && depth0.css_class) || helperMissing).call(depth0, (depth0 != null ? depth0.item : depth0), {"name":"css_class","hash":{},"data":data})))
    + "\"\n  id=\""
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.item_id : stack1), depth0))
    + "\">\n";
  stack1 = this.invokePartial(partials['ds-title-bar'], '  ', 'ds-title-bar', depth0, undefined, helpers, partials, data);
  if (stack1 != null) { buffer += stack1; }
  return buffer + "  <div class=\"ds-graph-holder "
    + escapeExpression(((helpers.height || (depth0 && depth0.height) || helperMissing).call(depth0, (depth0 != null ? depth0.item : depth0), {"name":"height","hash":{},"data":data})))
    + "\">\n    <svg class=\""
    + escapeExpression(((helpers.height || (depth0 && depth0.height) || helperMissing).call(depth0, (depth0 != null ? depth0.item : depth0), {"name":"height","hash":{},"data":data})))
    + "\"></svg>\n  </div>\n  <div class=\"ds-legend-holder\" id=\"ds-legend-"
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.item_id : stack1), depth0))
    + "\">\n  </div>\n</div>\n";
},"usePartial":true,"useData":true});

this["ds"]["templates"]["models"]["summation_table"] = Handlebars.template({"1":function(depth0,helpers,partials,data) {
  return "table-striped";
  },"compiler":[6,">= 2.0.0-beta.1"],"main":function(depth0,helpers,partials,data) {
  var stack1, lambda=this.lambda, escapeExpression=this.escapeExpression, helperMissing=helpers.helperMissing, buffer = "<div class=\"ds-item\" id=\""
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.item_id : stack1), depth0))
    + "\">\n";
  stack1 = this.invokePartial(partials['ds-title-bar'], '  ', 'ds-title-bar', depth0, undefined, helpers, partials, data);
  if (stack1 != null) { buffer += stack1; }
  buffer += "  <table class=\"table table-condensed ds-summation-table "
    + escapeExpression(((helpers.height || (depth0 && depth0.height) || helperMissing).call(depth0, (depth0 != null ? depth0.item : depth0), {"name":"height","hash":{},"data":data})))
    + " "
    + escapeExpression(((helpers.css_class || (depth0 && depth0.css_class) || helperMissing).call(depth0, (depth0 != null ? depth0.item : depth0), {"name":"css_class","hash":{},"data":data})))
    + "\n                ";
  stack1 = helpers['if'].call(depth0, ((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.striped : stack1), {"name":"if","hash":{},"fn":this.program(1, data),"inverse":this.noop,"data":data});
  if (stack1 != null) { buffer += stack1; }
  return buffer + "\">\n    <thead>\n      <tr>\n        <th>&nbsp;</th>\n        <th>current</th>\n        <th>min</th>\n        <th>max</th>\n        <th>mean</th>\n        <th>median</th>\n        <th>sum</th>\n      </tr>\n    </thead>\n    <tbody>\n    </tbody>\n  </table>\n</div>\n";
},"usePartial":true,"useData":true});

this["ds"]["templates"]["models"]["summation_table_row"] = Handlebars.template({"1":function(depth0,helpers,partials,data) {
  var helper, functionType="function", helperMissing=helpers.helperMissing, escapeExpression=this.escapeExpression;
  return "      <span class=\"ds-summation-color-cell\" style=\"background:"
    + escapeExpression(((helper = (helper = helpers.color || (depth0 != null ? depth0.color : depth0)) != null ? helper : helperMissing),(typeof helper === functionType ? helper.call(depth0, {"name":"color","hash":{},"data":data}) : helper)))
    + "\"></span>\n";
},"compiler":[6,">= 2.0.0-beta.1"],"main":function(depth0,helpers,partials,data) {
  var stack1, lambda=this.lambda, escapeExpression=this.escapeExpression, helperMissing=helpers.helperMissing, buffer = "<tr>\n    <th>\n";
  stack1 = helpers['if'].call(depth0, ((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.show_color : stack1), {"name":"if","hash":{},"fn":this.program(1, data),"inverse":this.noop,"data":data});
  if (stack1 != null) { buffer += stack1; }
  return buffer + "      "
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.series : depth0)) != null ? stack1.target : stack1), depth0))
    + "</th>\n    <td>"
    + escapeExpression(((helpers.format || (depth0 && depth0.format) || helperMissing).call(depth0, ((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.format : stack1), ((stack1 = ((stack1 = (depth0 != null ? depth0.series : depth0)) != null ? stack1.summation : stack1)) != null ? stack1.last : stack1), {"name":"format","hash":{},"data":data})))
    + "</td>\n    <td>"
    + escapeExpression(((helpers.format || (depth0 && depth0.format) || helperMissing).call(depth0, ((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.format : stack1), ((stack1 = ((stack1 = (depth0 != null ? depth0.series : depth0)) != null ? stack1.summation : stack1)) != null ? stack1.min : stack1), {"name":"format","hash":{},"data":data})))
    + "</td>\n    <td>"
    + escapeExpression(((helpers.format || (depth0 && depth0.format) || helperMissing).call(depth0, ((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.format : stack1), ((stack1 = ((stack1 = (depth0 != null ? depth0.series : depth0)) != null ? stack1.summation : stack1)) != null ? stack1.max : stack1), {"name":"format","hash":{},"data":data})))
    + "</td>\n    <td>"
    + escapeExpression(((helpers.format || (depth0 && depth0.format) || helperMissing).call(depth0, ((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.format : stack1), ((stack1 = ((stack1 = (depth0 != null ? depth0.series : depth0)) != null ? stack1.summation : stack1)) != null ? stack1.mean : stack1), {"name":"format","hash":{},"data":data})))
    + "</td>\n    <td>"
    + escapeExpression(((helpers.format || (depth0 && depth0.format) || helperMissing).call(depth0, ((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.format : stack1), ((stack1 = ((stack1 = (depth0 != null ? depth0.series : depth0)) != null ? stack1.summation : stack1)) != null ? stack1.median : stack1), {"name":"format","hash":{},"data":data})))
    + "</td>\n    <td>"
    + escapeExpression(((helpers.format || (depth0 && depth0.format) || helperMissing).call(depth0, ((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.format : stack1), ((stack1 = ((stack1 = (depth0 != null ? depth0.series : depth0)) != null ? stack1.summation : stack1)) != null ? stack1.sum : stack1), {"name":"format","hash":{},"data":data})))
    + "</td>\n  </tr>\n";
},"useData":true});

this["ds"]["templates"]["models"]["timeshift_summation_table"] = Handlebars.template({"1":function(depth0,helpers,partials,data) {
  return "table-striped";
  },"compiler":[6,">= 2.0.0-beta.1"],"main":function(depth0,helpers,partials,data) {
  var stack1, lambda=this.lambda, escapeExpression=this.escapeExpression, helperMissing=helpers.helperMissing, buffer = "<div class=\"ds-item\" id=\""
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.item_id : stack1), depth0))
    + "\">\n";
  stack1 = this.invokePartial(partials['ds-title-bar'], '  ', 'ds-title-bar', depth0, undefined, helpers, partials, data);
  if (stack1 != null) { buffer += stack1; }
  buffer += "  <table class=\"table table-condensed ds-timeshift-summation-table "
    + escapeExpression(((helpers.height || (depth0 && depth0.height) || helperMissing).call(depth0, (depth0 != null ? depth0.item : depth0), {"name":"height","hash":{},"data":data})))
    + " "
    + escapeExpression(((helpers.css_class || (depth0 && depth0.css_class) || helperMissing).call(depth0, (depth0 != null ? depth0.item : depth0), {"name":"css_class","hash":{},"data":data})))
    + "\n                ";
  stack1 = helpers['if'].call(depth0, ((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.striped : stack1), {"name":"if","hash":{},"fn":this.program(1, data),"inverse":this.noop,"data":data});
  if (stack1 != null) { buffer += stack1; }
  return buffer + "\">\n    <thead>\n      <tr>\n        <th></th>\n        <th>Now</th>\n        <th>"
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.shift : stack1), depth0))
    + " Ago</th>\n        <th>Delta</th>\n        <th>%</th>\n      </tr>\n    </thead>\n    <tbody/>\n  </table>\n</div>\n";
},"usePartial":true,"useData":true});

this["ds"]["templates"]["models"]["timeshift_summation_table_body"] = Handlebars.template({"compiler":[6,">= 2.0.0-beta.1"],"main":function(depth0,helpers,partials,data) {
  var stack1, helperMissing=helpers.helperMissing, escapeExpression=this.escapeExpression, lambda=this.lambda;
  return "<!-- TODO: configure which rows to include. Sum doesnt make sense for rates -->\n<tr>\n  <th>Average</th>\n  <td>"
    + escapeExpression(((helpers.format || (depth0 && depth0.format) || helperMissing).call(depth0, ((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.format : stack1), ((stack1 = (depth0 != null ? depth0.now : depth0)) != null ? stack1.mean : stack1), {"name":"format","hash":{},"data":data})))
    + "</td>\n  <td>"
    + escapeExpression(((helpers.format || (depth0 && depth0.format) || helperMissing).call(depth0, ((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.format : stack1), ((stack1 = (depth0 != null ? depth0.then : depth0)) != null ? stack1.mean : stack1), {"name":"format","hash":{},"data":data})))
    + "</td>\n  <td class=\""
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.diff : depth0)) != null ? stack1.mean_class : stack1), depth0))
    + "\">\n    "
    + escapeExpression(((helpers.format || (depth0 && depth0.format) || helperMissing).call(depth0, ((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.format : stack1), ((stack1 = (depth0 != null ? depth0.diff : depth0)) != null ? stack1.mean : stack1), {"name":"format","hash":{},"data":data})))
    + "\n  </td>\n  <td class=\""
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.diff : depth0)) != null ? stack1.mean_class : stack1), depth0))
    + "\">\n    "
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.diff : depth0)) != null ? stack1.mean_pct : stack1), depth0))
    + "\n  </td>\n</tr>\n<tr>\n  <th>Median</th>\n  <td>"
    + escapeExpression(((helpers.format || (depth0 && depth0.format) || helperMissing).call(depth0, ((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.format : stack1), ((stack1 = (depth0 != null ? depth0.now : depth0)) != null ? stack1.median : stack1), {"name":"format","hash":{},"data":data})))
    + "</td>\n  <td>"
    + escapeExpression(((helpers.format || (depth0 && depth0.format) || helperMissing).call(depth0, ((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.format : stack1), ((stack1 = (depth0 != null ? depth0.then : depth0)) != null ? stack1.median : stack1), {"name":"format","hash":{},"data":data})))
    + "</td>\n  <td class=\""
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.diff : depth0)) != null ? stack1.median_class : stack1), depth0))
    + "\">\n    "
    + escapeExpression(((helpers.format || (depth0 && depth0.format) || helperMissing).call(depth0, ((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.format : stack1), ((stack1 = (depth0 != null ? depth0.diff : depth0)) != null ? stack1.median : stack1), {"name":"format","hash":{},"data":data})))
    + "\n  </td>\n  <td class=\""
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.diff : depth0)) != null ? stack1.median_class : stack1), depth0))
    + "\">\n    "
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.diff : depth0)) != null ? stack1.median_pct : stack1), depth0))
    + "\n  </td>\n</tr>\n<tr>\n  <th>Min</th>\n  <td>"
    + escapeExpression(((helpers.format || (depth0 && depth0.format) || helperMissing).call(depth0, ((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.format : stack1), ((stack1 = (depth0 != null ? depth0.now : depth0)) != null ? stack1.min : stack1), {"name":"format","hash":{},"data":data})))
    + "</td>\n  <td>"
    + escapeExpression(((helpers.format || (depth0 && depth0.format) || helperMissing).call(depth0, ((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.format : stack1), ((stack1 = (depth0 != null ? depth0.then : depth0)) != null ? stack1.min : stack1), {"name":"format","hash":{},"data":data})))
    + "</td>\n  <td class=\""
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.diff : depth0)) != null ? stack1.min_class : stack1), depth0))
    + "\">\n    "
    + escapeExpression(((helpers.format || (depth0 && depth0.format) || helperMissing).call(depth0, ((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.format : stack1), ((stack1 = (depth0 != null ? depth0.diff : depth0)) != null ? stack1.min : stack1), {"name":"format","hash":{},"data":data})))
    + "\n  </td>\n  <td class=\""
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.diff : depth0)) != null ? stack1.min_class : stack1), depth0))
    + "\">\n    "
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.diff : depth0)) != null ? stack1.min_pct : stack1), depth0))
    + "\n  </td>\n</tr>\n<tr>\n  <th>Max</th>\n  <td>"
    + escapeExpression(((helpers.format || (depth0 && depth0.format) || helperMissing).call(depth0, ((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.format : stack1), ((stack1 = (depth0 != null ? depth0.now : depth0)) != null ? stack1.max : stack1), {"name":"format","hash":{},"data":data})))
    + "</td>\n  <td>"
    + escapeExpression(((helpers.format || (depth0 && depth0.format) || helperMissing).call(depth0, ((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.format : stack1), ((stack1 = (depth0 != null ? depth0.then : depth0)) != null ? stack1.max : stack1), {"name":"format","hash":{},"data":data})))
    + "</td>\n  <td class=\""
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.diff : depth0)) != null ? stack1.max_class : stack1), depth0))
    + "\">\n    "
    + escapeExpression(((helpers.format || (depth0 && depth0.format) || helperMissing).call(depth0, ((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.format : stack1), ((stack1 = (depth0 != null ? depth0.diff : depth0)) != null ? stack1.max : stack1), {"name":"format","hash":{},"data":data})))
    + "\n  </td>\n  <td class=\""
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.diff : depth0)) != null ? stack1.max_class : stack1), depth0))
    + "\">\n    "
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.diff : depth0)) != null ? stack1.max_pct : stack1), depth0))
    + "\n  </td>\n</tr>\n<tr>\n  <th>Sum</th>\n  <td>"
    + escapeExpression(((helpers.format || (depth0 && depth0.format) || helperMissing).call(depth0, ((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.format : stack1), ((stack1 = (depth0 != null ? depth0.now : depth0)) != null ? stack1.sum : stack1), {"name":"format","hash":{},"data":data})))
    + "</td>\n  <td>"
    + escapeExpression(((helpers.format || (depth0 && depth0.format) || helperMissing).call(depth0, ((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.format : stack1), ((stack1 = (depth0 != null ? depth0.then : depth0)) != null ? stack1.sum : stack1), {"name":"format","hash":{},"data":data})))
    + "</td>\n  <td class=\""
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.diff : depth0)) != null ? stack1.sum_class : stack1), depth0))
    + "\">\n    "
    + escapeExpression(((helpers.format || (depth0 && depth0.format) || helperMissing).call(depth0, ((stack1 = (depth0 != null ? depth0.item : depth0)) != null ? stack1.format : stack1), ((stack1 = (depth0 != null ? depth0.diff : depth0)) != null ? stack1.sum : stack1), {"name":"format","hash":{},"data":data})))
    + "\n  </td>\n  <td class=\""
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.diff : depth0)) != null ? stack1.sum_class : stack1), depth0))
    + "\">\n    "
    + escapeExpression(lambda(((stack1 = (depth0 != null ? depth0.diff : depth0)) != null ? stack1.sum_pct : stack1), depth0))
    + "\n  </td>\n</tr>\n";
},"useData":true});