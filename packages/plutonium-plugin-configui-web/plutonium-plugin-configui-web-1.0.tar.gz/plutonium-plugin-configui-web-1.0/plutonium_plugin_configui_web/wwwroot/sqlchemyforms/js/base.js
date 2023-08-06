
var sqlchemyforms = {
    widgets: {
        field: {},
    },
    validators: {},
    data_manager: function(handler) {
        var m_self = this;

        m_self.post = function(params)
        {
            $.post(params.url, JSON.stringify(params.data), function(raw) {
                var response = JSON.parse(raw);
                if(response.success) {
                    var pp = parsePath(params.url)
                    $.address.value(decodeURIComponent(pp.params.next));
                } else
                    params.on_error(response);
            });
        }

        m_self.get = function(url)
        {
            $.get(url, null, function(raw) {
                var response = JSON.parse(raw);

                handler.response(response);
            });
        }
    }
}
