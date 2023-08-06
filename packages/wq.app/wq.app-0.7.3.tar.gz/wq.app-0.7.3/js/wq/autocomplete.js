/*
 * wq.app 0.7.3 - wq/autocomplete.js
 * Simple AJAX autocomplete leveraging the HTML5 <datalist> element
 * (c) 2014-2015, S. Andrew Sheppard
 * https://wq.io/license
 */

define(['jquery', './pages', './json', './template', './spinner'],
function($, pages, json, tmpl, spin) {

// Exported module variable
var auto = {};

auto.template = '{{#list}}<option value="{{id}}">{{label}}</option>{{/list}}';

// Automatically register callbacks for every datalist
auto.init = function(template) {
    if (template)
        auto.template = template;
    pages.addRoute('.*', 's', _register);
    function _register(match, ui, params, hash, evt, $page) {
        $page.find('datalist').each(function(i, datalist) {
            /* jshint unused: false */
            auto.register($(datalist), $page);
        });
    }
};

// Register a jQuery-wrapped datalist element.  Changes to associated inputs
// will trigger an update.
auto.register = function($datalist, $scope) {
    var $input;
    if (!$scope)
        $scope = $datalist.parents('body');
    $input = $scope.find('input[list="' + $datalist.attr('id') + '"]');
    if (!$input.length || $input.data('registered')) {
        return;
    } else {
        $input.on('input.autocomplete', _update);
        $input.data('registered', true);
    }

    function _update() {
        auto.update($datalist, $input.val());
    }
};

var _cache = {};
auto.update = function($datalist, value) {
    var url = $datalist.data('url'),
        param = $datalist.data('query') || 'q',
        min = $datalist.data('min') || 3,
        exists = $datalist.find(
            'option[value="' + value.replace('"', "'") + '"]'
        ).length;

    // Only continue if a long enough value is present
    if (!value || value.length < min) {
        return;
    }

    // Compute full query url & re-use cached version if present
    url += url.indexOf('?') > -1 ? '&' : '?';
    url += param + '=' + value;
    if (_cache[url]) {
        auto.render($datalist, _cache[url]);
        return;
    }

    // Load results via AJAX
    if (!exists)
        spin.start();
    json.get(url, function(result) {
        if (!exists)
            spin.stop();
        if (!result.list)
            result = {'list': result};
        result.count = result.count || result.list.length;
        result.multi = result.count > 1;
        _cache[url] = result;
        auto.render($datalist, result);
    });

};

// Update <datalist> HTML with new <options>
auto.render = function($datalist, result) {
    var $options = $datalist.find('option'),
        data = result.list,
        $tmpdl, $tmpopts, last;

    // Reset list if no data present
    if (!data || !data.length) {
        $datalist.empty();
        return;
    }

    // Don't update if list is the same as before
    if ($options.length == data.length) {
        $tmpdl = $("<datalist>");
        $tmpdl.append(tmpl.render(auto.template, result));
        $tmpopts = $tmpdl.find('option');
        last = data.length - 1;
        if ($options[0].value == $tmpopts[0].value &&
                $options[last].value == $tmpopts[last].value) {
            return;
        }
    }

    // Render data into template
    $datalist.empty().append(tmpl.render(auto.template, result));
};

return auto;

});
