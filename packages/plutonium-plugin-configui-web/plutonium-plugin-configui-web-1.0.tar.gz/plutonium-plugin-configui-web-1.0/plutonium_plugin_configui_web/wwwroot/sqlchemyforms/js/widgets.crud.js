
sqlchemyforms.widgets.crud = function(cont, api_path, models, lm)
{
    var m_cont = cont;
    var m_self = this;
    var m_api_path = api_path;
    var m_models = models;
    var m_last_path = '';
    var m_data_manager = new sqlchemyforms.data_manager(m_self);

    m_self.response = function(resp)
    {
        m_self[resp.method](resp)

        $('.selectpicker').selectpicker();

        $("input[type='checkbox']").bootstrapSwitch();
    }

    m_self.load = function(path)
    {
        m_last_path = m_api_path + path;
        m_data_manager.get(m_api_path + path);
    }

    m_self.reload = function()
    {
        m_self.load(m_last_path);
    }

    function get_model_desc(table)
    {
        if(table in m_models)
            return m_models[table]

        throw (table + ' is missing from model definitions');
    }

    m_self.do_create = function(resp)
    {
        resp.data.title = 'create_new_' + resp.data.name;
        m_cont.set(sqlchemyforms.widgets.form(resp.data, get_model_desc(resp.table).form, m_data_manager, lm));
    }

    m_self.do_read = function(resp)
    {
        var desc = get_model_desc(resp.table).view;
        var rows = []

        foreach(desc.fields, function(field) {
            var cell = td()
            if('renderer' in field)
                cell.set(field.renderer(resp.data[field.name]))
            else
                cell.set(resp.data[field.name])

            rows.push(tr(
                td({lm_key: field.name}),
                cell
            ));
        });

        //TODO: remove this mess
        var read_param = {}
        read_param[resp.primary_key] = resp.data[resp.primary_key]
        var qs = {next: makePath([resp.table, 'read'], read_param)}
        qs[resp.primary_key] = resp.data[resp.primary_key]
        var update_link = makePath([resp.table, 'update'], qs);
        qs.next = makePath([resp.table, 'list']);
        var delete_link = makePath([resp.table, 'delete'], qs);

        var cont = div(
            h2(
                resp.data[desc.title],
                ' ',
                a({href: update_link, class: 'btn btn-primary btn-xs'},
                    span({class: 'glyphicon glyphicon-pencil'}),
                    ' ',
                    span({lm_key: 'Edit'})
                ),
                ' ',
                a({href: delete_link, class: 'btn btn-danger btn-xs'},
                    span({class: 'glyphicon glyphicon-trash'}),
                    ' ',
                    span({lm_key: 'Delete'})
                )
            ),
            table({class: 'table table-striped table-hover'}, tbody(rows))
        );

        m_cont.set(cont);
    }

    m_self.do_update = function(resp)
    {
        resp.data.title = 'update_' + resp.data.name;
        var form = sqlchemyforms.widgets.form(resp.data, get_model_desc(resp.table).form, m_data_manager, lm);
        m_cont.set(form);
    }

    m_self.do_delete = function(resp)
    {
        var next = decodeURIComponent($.address.parameter('next'));

        var del = function() {

            m_data_manager.post({
                url: m_api_path + decodeURIComponent($.address.value()),
                data: {},
                on_error: function(r) {
                    BootstrapDialog.show({
                        type: BootstrapDialog.TYPE_DANGER,
                        title: span({lm_key: 'error_on_delete'}),
                        message: span({lm_key: 'delete_error_message'}),
                        onhide: function(dialogRef) {
                            $.address.value(next);
                        }
                    });
                }
            })
        }

        m_cont.set(
            div({class: "alert alert-danger", role: "alert"},
                span({class: 'glyphicon glyphicon-question-sign'}),
                ' ',
                span({lm_key: 'delete_confirm'})
            ),
            a({href: '#', class: "btn btn-danger", onclick: del}, span({class: 'glyphicon glyphicon-ok-sign'}),
                ' ',
                span({lm_key: 'ok'})
            ),
            ' ',
            a({href: next, class: "btn btn-primary"}, span({class: 'glyphicon glyphicon-remove-sign'}), ' ', span({lm_key: 'cancel'}))
        );
    }

    m_self.do_list = function(resp)
    {
        m_cont.set(sqlchemyforms.widgets.table(resp, get_model_desc(resp.table).table));
    }
}
