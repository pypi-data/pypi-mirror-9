$(document).ready(function() {
    $('a#header-logout').click(function(e) {
        e.stopPropagation();
        dcbase.popupAjaxForm({
            url: logout_url,
            small: true
        })
    });
});

var dcbase = {
    createUrl: function (urlPattern) {
        var parts = urlPattern.split('0');
        var finalUrl = '';
        for (var i = 0; i < (parts.length - 1); i++) {
            finalUrl += parts[i];
            finalUrl += arguments[i + 1];
        }
        finalUrl += parts[parts.length - 1];
        return finalUrl;
    },

    createUserTypeahead: function(inputElement) {
        var usersFetch = new Bloodhound({
            datumTokenizer: Bloodhound.tokenizers.obj.whitespace('value'),
            queryTokenizer: Bloodhound.tokenizers.whitespace,
            remote: '/accounts/match/?q=%QUERY'
        });
        usersFetch.initialize();

        $(inputElement).typeahead(null, {
            displayKey: 'value',
            source: usersFetch.ttAdapter(),
            templates: {
                suggestion: function(data) {
                    return '<img class="gravatar" src="' + data.avatar_url + '" width="25" height="25" /> ' + data.value;
                }
            }
        });
    },

    popupAjaxForm: function(options) {
        options = $.extend({
            small: false
        }, options);

        var initialContent = $('<div class="modal-body">' +
            '<div style="width:32px; margin: auto"><img src="' + static_root + '/img/wait-lg.gif" /></div>' +
            '</div>'
        );
        var content = $('<div />').addClass('modal-content');
        content.append(initialContent);
        var dialog = $('<div />').addClass('modal-dialog');
        if (options.small) {
            dialog.addClass('modal-sm');
        }
        dialog.append(content);
        var modal = $('<div />').addClass('modal fade');
        modal.append(dialog);
        $('#content-wrapper').append(modal);
        modal.modal('show');
        modal.on('hidden.bs.modal', function(e) {
            $(e.target).remove();
        });
        var setupAjaxForm = function() {
            if (options.afterLoad) {
                options.afterLoad(content);
            }
            content.find('form').ajaxForm({
                target: content,
                success: function(response, status, xhr, form) {
                    if (xhr.responseJSON) {
                       switch(xhr.responseJSON.action) {
                           case 'reload':
                               window.location.reload();
                               break;
                           case 'close':
                               modal.modal('hide');
                               break;
                           case 'redirect':
                               window.location = xhr.responseJSON.url;
                               break;
                       }
                    }
                    setupAjaxForm();
                }
            });
        };
        content.load(options.url, setupAjaxForm);
    }
};
