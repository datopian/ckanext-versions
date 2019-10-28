/* API for ckanext-versions */

"use strict";

ckan.module('dataset_version_controls', function ($) {

    return {

        _apiBaseUrl: null,
        _packageId: null,
        _packageUrl: null,

        initialize: function ()
        {
            $.proxyAll(this, /_on/);
            this._apiBaseUrl = this.options.apiUrl;
            this._packageId = this.options.packageId;
            this._packageUrl = this.options.packageUrl;
            this._linkResources = (this.options.linkResources == 'True');

            if(this._linkResources){
                this.$(".modal-body").append(
                    ['<div class="form-group">',
                    '<span>',
                    '<i class="fa fa-info-circle"></i>',
                    'External resources are not guaranteed to be unmutable.',
                    '</span>',
                    '</div>'].join('\n')
                );
            };

            this.$('.delete-version-btn').on('click', this._onDelete);
            this.$('.create-version-form').on('submit', this._onCreate);
        },

        _onDelete: function (evt)
        {
            let versionName = $(evt.target).data('version-name');
            let versionId = $(evt.target).data('version-id');
            if (confirm("Are you sure you want to delete the version \"" + versionName + "\" of this dataset?")) {
                return this._delete(versionId);
            }
        },

        _onCreate: function (evt)
        {
            let versionName = evt.target.querySelector("input[name=version_name]").value.trim();
            let description = evt.target.querySelector("textarea[name=details]").value.trim();

            evt.preventDefault();
            return this._create(this._packageId, versionName, description);
        },

        _apiPost: function (action, params)
        {
            let url = this._apiBaseUrl + action;
            return fetch(url, {
                method: 'POST',
                body: JSON.stringify(params),
                headers: {
                    'Content-Type': 'application/json'
                }
            });
        },

        _delete: function (versionId) {
            const action = 'dataset_version_delete';
            let params = {
                id: versionId
            };

            this._apiPost(action, params)
                .then(function (response) {
                    if (response.status !== 200) {
                        response.json().then(function (jsonResponse) {
                            alert("There was an error deleting the dataset version.");
                            console.error({params, jsonResponse});
                        });
                    } else {
                        location.href = this._packageUrl;
                    }
                }.bind(this));
        },

        _create: function (datasetId, versionName, description) {
            const action = 'dataset_version_create';
            let params = {
                dataset: datasetId,
                name: versionName,
                description: description
            };

            this._apiPost(action, params)
                .then(function (response) {
                    if (response.status !== 200) {
                        response.json().then(function (jsonResponse) {
                            alert("There was an error creating the dataset version.");
                            console.error({params, jsonResponse});
                        });
                    } else {
                        location.reload();
                    }
                });
        }

    };

});

