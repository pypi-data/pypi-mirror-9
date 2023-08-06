
$.extend(sqlchemyforms.widgets, {
    form: function(data, desc, data_manager, lm) {

        var cont = form({
            class: 'form-horizontal',
            action: data.action,
            method: data.method
        });

        function generate_rows()
        {
            var rows = [];

            foreach(desc.fields, function(field) {
                var widget = data.widgets[field.name]

                widget.validators = []

                widget.validate = function(value, form_data) {
                    var errors = []
                    foreach(this.validators, function(validator) {
                        var res = validator(value, form_data)
                        if(res !== true)
                            errors.push(res);
                    })
                    return errors;
                }

                if('validators' in field) {
                    foreach(field.validators, function(type) {
                        sqlchemyforms.validators[type](widget);
                    });
                }

                if(widget.type == 'hidden') {
                    rows.push(sqlchemyforms.widgets.field.text(widget, field))
                    return;
                }

                widget.id = randomString(8, 'id');

                var row = div({class: 'form-group'},
                    label({'for': widget.id, class: 'col-lg-2 control-label', lm_key: widget.name}),
                    div({class: 'col-lg-10'}, sqlchemyforms.widgets.field[widget.type](widget, field))
                )

                row.p('id', widget.id + '_row');

                rows.push(row);
            });

            rows.push(
                div({class: 'form-group'},
                    div({class: 'col-lg-10 col-lg-offset-2'},
                        button({type: 'submit', class: 'btn btn-primary', lm_key: 'save'})
                    )
                )
            )
            return rows;
        }

        cont.serialize = function()
        {
            return $(this).serializeJSON({
                parseWithFunction: function(val, inputName) {
                    if(val === "") return null;
                    return val;
                },
                parseAll: true,
                checkboxUncheckedValue: "false",
            });
        }

        cont.validate = function(post_data)
        {
            var local_errors = {};

            foreach(desc.fields, function(field) {
                var widget = data.widgets[field.name]
                var errors = widget.validate(post_data[field.name], post_data);
                if(errors.length)
                    local_errors[field.name] = errors;
            });

            return local_errors;
        }

        cont.add(fieldset(legend({lm_key: data.title}), generate_rows()))

        cont.onsubmit = function(event) {

            var post_data = cont.serialize();

            var local_errors = cont.validate(post_data);

            foreach(desc.fields, function(field) {
                var widget = data.widgets[field.name];

                if(field.name in local_errors) {
                    $('#' + widget.id + '_row').addClass('has-error');
                    $('#' + widget.id).popover({
                        placement: 'left', html: true, trigger: 'hover',
                        content: function() {
                            var list = ul();
                            foreach(local_errors[field.name], function(err) {
                                list.add(li(lm.get(err)));
                            })
                            return div(list).innerHTML;
                        },
                        title: function(){
                            return div(lm.get('bad_field', {name: lm.get(field.name)})).innerHTML;
                        }});
                } else {
                    $('#' + widget.id + '_row').removeClass('has-error');
                    $('#' + widget.id).popover('destroy');
                }
            });

            if(!Map.empty(local_errors)){
                console.debug('Errors in form:', local_errors);
                return false;
            }

            console.debug('POST data:', post_data);

            data_manager.post({
                url: data.action,
                data: post_data,
                on_error: function(res) {
                    console.log('error!', res)
                }
            })
            return false;
        }

        return cont;
    },
    table: function(resp, desc) {
        var cont = table({class: 'table table-striped table-hover'});

        var body = tbody();
        var cols = [];

        if('width' in desc)
            $(cont).width(desc.width)

        foreach(desc.columns, function(col) {
            var cell = th({lm_key: col.name})
            if('width' in col)
                $(cell).width(col.width);
            if('class' in col)
                cell.addClass(col.class);
            cols.push(cell)
        });

        cont.add(thead(tr(cols, th({style: 'width: 70px'}))));

        foreach(resp.data.rows, function(row) {
            var cells = [];
            foreach(desc.columns, function(col) {
                var cell = td();
                if('renderer' in col)
                    cell.set(col.renderer(row[col.name], row))
                else
                    cell.set(row[col.name])

                if('class' in col)
                    cell.addClass(col.class);

                cells.push(cell)
            })
            var qs = {next: makePath([resp.table, 'list'])}
            qs[resp.primary_key] = row[resp.primary_key]
            var update_link = makePath([resp.table, 'update'], qs);
            var delete_link = makePath([resp.table, 'delete'], qs);

            body.add(tr(
                cells,
                td(
                    a({href: update_link, class: 'btn btn-primary btn-xs'}, span({class: 'glyphicon glyphicon-pencil'})),' ',
                    a({href: delete_link, class: 'btn btn-danger btn-xs'}, span({class: 'glyphicon glyphicon-trash'}))
                )
            ));
        });

        cont.add(body);

        return cont;
    }
});
