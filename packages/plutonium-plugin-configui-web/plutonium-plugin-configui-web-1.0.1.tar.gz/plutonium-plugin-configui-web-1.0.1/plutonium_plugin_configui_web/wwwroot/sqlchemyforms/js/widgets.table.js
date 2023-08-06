$.extend(sqlchemyforms.widgets, {
    table: function(resp, desc) {
        var cont = table({class: 'table table-striped table-hover'});

        var body = tbody();
        var cols = [];

        if('width' in desc)
            $(cont).width(desc.width)

        foreach(desc.columns, function(col) {
            var cell = th({style: 'white-space: nowrap;'}, span({lm_key: col.name}))
            if('width' in col)
                $(cell).width(col.width);
            if('class' in col)
                cell.addClass(col.class);

            if(resp.data.columns[col.name].sortable) {
                var sortlabel = span({class: 'glyphicon glyphicon-chevron-down'})
                cell.add(' ', sortlabel);
                if(col.name == resp.data.sort)
                    sortlabel.addClass('show_sort')
            }

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
    },
})
