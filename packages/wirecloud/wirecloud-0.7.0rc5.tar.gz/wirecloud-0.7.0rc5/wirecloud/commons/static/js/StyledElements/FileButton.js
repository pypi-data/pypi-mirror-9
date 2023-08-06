/*
 *     Copyright (c) 2015 CoNWeT Lab., Universidad Politécnica de Madrid
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

/*global StyledElements*/

(function () {

    "use strict";

    var FileButton, onchange;

    onchange = function onchange() {
        this.events.fileselect.dispatch(this, this.getValue());
    };

    FileButton = function FileButton(options) {
        var defaultOptions = {
            'multiple': true
        };
        options = StyledElements.Utils.merge(defaultOptions, options);

        StyledElements.StyledButton.call(this, options);

        Object.defineProperty(this, 'inputElement', {value: document.createElement("input")});
        this.inputElement.setAttribute("type", "file");
        this.inputElement.setAttribute("tabindex", "-1");
        this.inputElement.multiple = options.multiple;
        this.wrapperElement.appendChild(this.inputElement);

        this.events.fileselect = new StyledElements.Event();

        /* Internal events */
        this._onchange = onchange.bind(this);

        this.inputElement.addEventListener('change', this._onchange, true);
    };
    FileButton.prototype = new StyledElements.StyledButton();

    FileButton.prototype.getValue = function getValue() {
        return this.inputElement.files;
    };

    FileButton.prototype.destroy = function destroy() {

        this.inputElement.removeEventListener('change', this._onchange, true);

        delete this._onchange;

        StyledElements.StyledButton.prototype.destroy.call(this);
    };

    StyledElements.FileButton = FileButton;

})();
