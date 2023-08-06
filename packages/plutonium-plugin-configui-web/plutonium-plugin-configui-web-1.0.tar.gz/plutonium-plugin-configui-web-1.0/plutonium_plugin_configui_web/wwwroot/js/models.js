
var models = {
    feeds: {
        table: {
            columns: [
                {
                    name: 'id',
                    width: 30,
                    renderer: function(value) {
                        return a({href: '/feeds/read?id='+value}, value)
                    }
                },{
                    name: 'enabled',
                    width: 10,
                    class: 'text-center',
                    renderer: function(value) {
                        return span({class: 'glyphicon glyphicon-'+(value?'ok':'remove')})
                    }
                },{
                    name: 'name',
                    renderer: function(value, row) {
                        return a({href: '/feeds/read?id='+row.id}, value)
                    }
                },{
                    name: 'output',
                    width: 100,
                },{
                    name: 'update_interval',
                    width: 150,
                    class: 'text-right',
                    renderer: function(value) {
                        return format_timedelta(value);
                    }
                },{
                    name: 'filters',
                    width: 50,
                    class: 'text-right'
                }
            ],
            width: 700
        },
        view: {
            title: 'name',
            fields: [
                {
                    name: 'enabled',
                    renderer: function(value) {
                        return span({class: 'glyphicon glyphicon-'+(value?'ok':'remove')})
                    }
                },{
                    name: 'url',
                    renderer: function(value) {
                        return a({href: value}, value)
                    }
                },{
                    name: 'update_interval',
                    renderer: function(value) {
                        return format_timedelta(value);
                    }
                },{
                    name: 'target_path_pattern'
                },{
                    name: 'output',
                    renderer: function(value) { //TODO: maybe some generic function to handle relationship like fields...
                        return a({href: '/outputs/read?id='+value.id}, value.name)
                    }
                },{
                    name: 'filters',
                    renderer: function(value) { //TODO: maybe some generic function to handle relationship like fields...
                        var items = []
                        foreach(value, function(filter) {
                            items.push(span(
                                {class: 'label label-primary', style: 'margin-right: 5px;'},
                                a({href: '/filters/read?id='+filter.id}, filter.name)
                            ))
                        });
                        return items;
                    }
                },{
                    name: 'torrents',
                    renderer: function(value) {
                        var rows = []
                        foreach(value, function(torrent) {
                            rows.push(tr(
                                td(torrent.added),
                                td(torrent.title)
                            ))
                        });
                        var tbl = table({class: 'table table-striped table-hover'},
                            thead(tr(th({style: 'min-width: 150px', lm_key: 'added'}), th({lm_key: 'title'}))),
                            tbody(rows)
                        )._hide();
                        var note = a({href: '#', lm_key: 'feed_torrent_notes', onclick: function() { tbl._show(!tbl.isShown()); }});

                        return [{style: 'max-width: 850px'}, note, tbl];
                    }
                }
            ],
        },
        form: {
            fields: [
                {
                    name: 'id'
                },{
                    name: 'url',
                    validators: ['required', 'regexp'],
                },{
                    name: 'name',
                    validators: ['required'],
                },{
                    name: 'enabled'
                },{
                    name: 'output',
                    option_renderer: function(value) {
                        return value.name
                    }
                },{
                    name: 'update_interval',
                    validators: ['required'/*, 'integer'*/],
                },{
                    name: 'target_path_pattern',
                    validators: ['required'],
                },{
                    name: 'filters',
                    option_renderer: function(value) {
                        return value.name
                    }
                }
            ]
        }
    },
    filters: {
        table: {
            columns: [
                {
                    name: 'id',
                    width: 30,
                    renderer: function(value) {
                        return a({href: '/filters/read?id='+value}, value)
                    }
                },{
                    name: 'name',
                    renderer: function(value, row) {
                        return a({href: '/filters/read?id='+row.id}, value)
                    }
                },{
                    name: 'pattern',
                },{
                    name: 'source_node',
                },{
                    name: 'type',
                }
            ],
            width: 700
        },
        view: {
            title: 'name',
            fields: [
                {
                    name: 'pattern',
                },{
                    name: 'source_node',
                },{
                    name: 'type',
                }
            ],
        },
        form: {
            fields: [
                {
                    name: 'id'
                },{
                    name: 'name',
                    validators: ['required'],
                },{
                    name: 'pattern',
                    validators: ['required'],
                },{
                    name: 'source_node',
                    validators: ['required'],
                },{
                    name: 'type'
                }
            ]
        }
    },
    outputs: {
        table: {
            columns: [
                {
                    name: 'id',
                    width: 30,
                    renderer: function(value) {
                        return a({href: '/outputs/read?id='+value}, value)
                    }
                },{
                    name: 'name',
                    renderer: function(value, row) {
                        return a({href: '/outputs/read?id='+row.id}, value)
                    }
                },{
                    name: 'type',
                }
            ],
            width: 700
        },
        view: {
            title: 'name',
            fields: [
                {
                    name: 'type',
                },{
                    name: 'params',
                    renderer: function(value) {
                        return pre(JSON.stringify(value, null, 4));
                    }
                }
            ],
        },
        form: {
            fields: [
                {
                    name: 'id'
                },{
                    name: 'name',
                    validators: ['required'],
                },{
                    name: 'type'
                },{
                    name: 'params',
                    validators: ['struct'],
                }
            ]
        }
    },
}


