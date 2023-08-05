cw.cubes.squareui = new Namespace('cw.cubes.squareui');

$.extend(cw.cubes.squareui, {
    storeLocalData: function (key, value) {
        localStorage.setItem(key, JSON.stringify(value));
    },

    getLocalData: function (key) {
        var data = localStorage.getItem(key);
        if (data !== undefined) {
            data = JSON.parse(data);
        }
        return data;
    },

    toggleLeftColumn: function (toggle) {
        var $contentCol = $('#main-center');
        var $asideCols = $(".cwjs-aside");
        if ($asideCols.length) {
            var collapsendContentClass = 'col-md-' + (12 - $asideCols.length * 3);
            var fullContentClass = 'col-md-12';
            var displayAsideboxes = cw.cubes.squareui.getLocalData('asideboxes');
            if (toggle === undefined) {
                displayAsideboxes = $asideCols.hasClass('hidden');
                cw.cubes.squareui.storeLocalData('asideboxes', displayAsideboxes);
            }
            if (displayAsideboxes === false) {
                $asideCols.addClass('hidden');
                $contentCol.removeClass(collapsendContentClass).addClass(fullContentClass);
            } else {
                $asideCols.removeClass('hidden');
                $contentCol.removeClass(fullContentClass).addClass(collapsendContentClass);
            }
        }
    }

});

$(document).ready(function () {
    if ($('#cw-aside-toggle').length) {
        // if HideAsidesBar component is activated
        var displayAsideboxes = cw.cubes.squareui.getLocalData('asideboxes');
        if (displayAsideboxes !== undefined) {
            cw.cubes.squareui.toggleLeftColumn(displayAsideboxes);
        }
    }
});
