
$.extend(sqlchemyforms.validators, {
    required: function(widget) {
        widget.validators.push(function(value){
            return value ? true : 'required'
        });
    },
    regexp: function(widget) {
        var pattern = new RegExp(widget.regexp);

        widget.validators.push(function(value){
            return pattern.test(value) ? true : widget.error_message;
        });
    },
});
