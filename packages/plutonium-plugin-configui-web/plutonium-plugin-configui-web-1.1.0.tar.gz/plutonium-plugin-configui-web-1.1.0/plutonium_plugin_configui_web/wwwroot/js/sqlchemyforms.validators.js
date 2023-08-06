
$.extend(sqlchemyforms.validators, {
    struct: function(widget){
        widget.validators.push(function(value, post_data){
            var struct = widget.depends_on ? widget.struct[post_data[widget.depends_on]] : widget.struct;

            console.log(struct);
            return true;
        })
    }
});
