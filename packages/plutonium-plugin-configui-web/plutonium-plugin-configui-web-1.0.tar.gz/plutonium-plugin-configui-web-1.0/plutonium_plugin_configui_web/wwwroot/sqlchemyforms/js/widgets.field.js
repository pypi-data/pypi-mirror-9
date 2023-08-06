
$.extend(sqlchemyforms.widgets.field, {
    select: function(data, field) {
        var name = data.name;
        if(data.multiple)
            name += '[]'

        var cont = select({class: 'selectpicker', name:  name});
        var value = data.value;
        if(data.multiple)
            cont.add({multiple: ''});
        else
            value = [value]

        foreach(data.options, function(title, key) {
            var op = option({value: key}, 'option_renderer' in field ? field.option_renderer(title) : title);

            // im very tired of this type shit...
            key = isNaN(parseInt(key)) ? key : parseInt(key);
            if(value.indexOf(key) != -1)
                op.add({selected: ''})
            cont.add(op)
        })

        // if not selected any options this will add an empty array
        if(data.multiple)
            cont = [input({type:'hidden', name: data.name+':array', value: '[]'}), cont]

        return cont;
    },
    checkbox: function(data) {
        var checked = data.value;
        data.value = '1';
        var inp = sqlchemyforms.widgets.field.text(data);
        inp.checked = checked;
        return inp;
    },
    text: function(data) {
        var inp = input({
            class: 'form-control',
            id: data.id,
            value: data.value ? data.value : data.default,
            type: data.type,
            name: data.name
        });
        if('lm_key' in data)
            inp.p('lm_key', data.lm_key)
        if('lm_attr' in data)
            inp.p('lm_attr', data.lm_attr)
        return inp;
    },
    integer: function(data) {
        return sqlchemyforms.widgets.field.text(data);
    }
});
