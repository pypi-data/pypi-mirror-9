
$.extend(sqlchemyforms.widgets.field, {
    struct: function(data){
        function fetch(obj, cont, parent_name, parent_value)
        {
            var body = div({class: 'form-horizontal'});

            foreach(obj, function(desc) {
                var name = desc.name;
                var type = desc.type;
                var id = randomString(8, 'id');
                var cell = div({class: 'col-lg-10'});

                var value = parent_value ? (name in parent_value ? parent_value[name] : '') : '';

                if(desc.nodes != null)
                    fetch(desc.nodes, cell, parent_name + name + '][', value);
                else {
                    desc.validators = [];

                    cell.set(sqlchemyforms.widgets.field[type]({
                        id: id,
                        value: value,
                        default: desc.default,
                        type: type,
                        value_type: desc.value_type,
                        name: parent_name + name + ']'
                    }))
                }

                body.add(div({class: 'form-group'}, label({'for': id, class: 'col-lg-2 control-label', lm_key: name}), cell));
            });
            cont.add(body);
        }

        var cont = div();

        foreach(data.struct, function(desc, name) {
            var desc_cont = div({id: data.name + '_' + name});
            fetch(desc, desc_cont, data.name + '[', data.value);
            cont.add(desc_cont)
        })

        return cont;
    }
});
