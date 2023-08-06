/*
 *     Copyright (c) 2012-2015 CoNWeT Lab., Universidad Politécnica de Madrid
 *
 *     This file is part of Wirecloud Platform.
 *
 *     Wirecloud Platform is free software: you can redistribute it and/or
 *     modify it under the terms of the GNU Affero General Public License as
 *     published by the Free Software Foundation, either version 3 of the
 *     License, or (at your option) any later version.
 *
 *     Wirecloud is distributed in the hope that it will be useful, but WITHOUT
 *     ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
 *     FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public
 *     License for more details.
 *
 *     You should have received a copy of the GNU Affero General Public License
 *     along with Wirecloud Platform.  If not, see
 *     <http://www.gnu.org/licenses/>.
 *
 */

/*global gettext, LayoutManagerFactory, StyledElements, Wirecloud*/

(function () {

    "use strict";

    var OfferingResourcePainter = function OfferingResourcePainter() {
    };

    var onInstallClick = function onInstallClick(resource, catalogue, offering_entry, button) {
        var layoutManager, local_catalogue_view, url;

        button.disable();

        local_catalogue_view = LayoutManagerFactory.getInstance().viewsByName.myresources;
        layoutManager = LayoutManagerFactory.getInstance();
        layoutManager._startComplexTask(gettext("Importing resource into local repository"), 3);
        layoutManager.logSubTask(gettext('Uploading resource'));

        resource.install({
            onSuccess: function () {
                LayoutManagerFactory.getInstance().logSubTask(gettext('Resource installed successfully'));
                LayoutManagerFactory.getInstance().logStep('');

                offering_entry.update_buttons();

                catalogue.viewsByName.search.mark_outdated();
                local_catalogue_view.viewsByName.search.mark_outdated();
            },
            onFailure: function (msg) {
                Wirecloud.GlobalLogManager.log(msg);
                (new Wirecloud.ui.MessageWindowMenu(msg, Wirecloud.constants.LOGGING.ERROR_MSG)).show();
            },
            onComplete: function () {
                button.enable();
                LayoutManagerFactory.getInstance()._notifyPlatformReady();
            }
        });
    };

    var onUninstallClick = function onUninstallClick(resource, catalogue, offering_entry, button) {
        var layoutManager, local_catalogue_view, url;

        button.disable();

        local_catalogue_view = LayoutManagerFactory.getInstance().viewsByName.myresources;
        layoutManager = LayoutManagerFactory.getInstance();
        layoutManager._startComplexTask(gettext("Uninstalling resource from local repository"), 3);
        layoutManager.logSubTask(gettext('Uninstalling resource'));

        local_catalogue_view.catalogue.uninstallResource(resource.wirecloud, {
            onSuccess: function () {
                LayoutManagerFactory.getInstance().logSubTask(gettext('Resource uninstalled successfully'));
                LayoutManagerFactory.getInstance().logStep('');

                offering_entry.update_buttons();

                catalogue.viewsByName.search.mark_outdated();
                local_catalogue_view.viewsByName.search.mark_outdated();
            },
            onFailure: function (msg) {
                Wirecloud.GlobalLogManager.log(msg);
                (new Wirecloud.ui.MessageWindowMenu(msg, Wirecloud.constants.LOGGING.ERROR_MSG)).show();
            },
            onComplete: function () {
                button.enable();
                LayoutManagerFactory.getInstance()._notifyPlatformReady();
            }
        });
    };

    OfferingResourcePainter.prototype.paint = function paint(offering, dom_element, catalogue, offering_entry) {
        var i, resource, btn_group, button, details_button, resource_entry;

        offering_entry.resources = new StyledElements.ModelTable([
                {
                    "field": ["resource", "name"],
                    "label": Wirecloud.Utils.gettext('Name'),
                    "contentBuilder": function (entry) {
                        var fragment = new StyledElements.Fragment();

                        var title = document.createElement('h5');
                        title.textContent = entry.resource.name;
                        fragment.appendChild(title);
                        if ('type' in resource && !('install' in resource)) {
                            var error_label = document.createElement('span');
                            error_label.className = 'label label-danger';
                            error_label.textContent = Wirecloud.Utils.gettext('missing WireCloud metadata');
                            title.appendChild(error_label);
                        }
                        var description = document.createTextNode(entry.resource.description);
                        fragment.appendChild(description);
                        return fragment;
                    }
                },
                {
                    "label": Wirecloud.Utils.gettext('Actions'),
                    "width": "css",
                    "class": "wc-fiware-offering-resources-buttons-column",
                    "sortable": false,
                    "contentBuilder": function (entry) {
                        var resource = entry.resource;

                        if (entry.install_button != null) {
                            entry.install_button.clearClassName().clearEventListeners('click');
                            if (Wirecloud.LocalCatalogue.resourceExistsId(resource.id)) {
                                entry.install_button.addClassName('btn-danger').setLabel(gettext('Uninstall'));
                                entry.install_button.addEventListener('click', onUninstallClick.bind(null, resource, catalogue, offering_entry));
                                entry.details_button.enable();
                            } else {
                                entry.install_button.addClassName('btn-primary').setLabel(gettext('Install'));
                                entry.install_button.addEventListener('click', onInstallClick.bind(null, resource, catalogue, offering_entry));
                                entry.details_button.disable();
                            }
                        }
                        return entry.buttons;
                    }
                }
            ], {
                pageSize: 0,
                'class': 'offering_resource_list'
            }
        );
        dom_element.appendChild(offering_entry.resources);

        offering_entry.update_resource_buttons = function update_resource_buttons() {
            this.resources.source.refresh();
        };

        for (i = 0; i < offering.resources.length; i += 1) {
            btn_group = document.createElement('div');
            btn_group.className = 'btn-group';
            resource = offering.resources[i];
            resource_entry = {resource: resource, buttons: btn_group};

            if ('url' in resource) {

                if ('install' in resource) {

                    button = new StyledElements.StyledButton({text: ''});
                    button.insertInto(btn_group);
                    details_button = new StyledElements.StyledButton({text: gettext('Details')});
                    details_button.addEventListener('click', function () {
                        var myresources_view = LayoutManagerFactory.getInstance().viewsByName.myresources;
                        myresources_view.createUserCommand('showDetails', this, {version: this.version})();
                    }.bind(resource));
                    details_button.insertInto(btn_group);
                    resource_entry.install_button = button;
                    resource_entry.details_button = details_button;

                } else {
                    button = new StyledElements.StyledButton({'class': 'btn-info', text: gettext('Download')});
                    button.insertInto(btn_group);
                }
            }
            offering_entry.resources.source.addElement(resource_entry);
        }
    };

    Wirecloud.FiWare.ui.OfferingResourcePainter = OfferingResourcePainter;

})();
