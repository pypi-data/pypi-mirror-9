function dGE(id){return document.getElementById(id);}

function def(p_var, p_default)
{
    return (typeof p_var == 'undefined') ? p_default : p_var;
}
function pathInfo(filename)
{
    var arr = filename.split('.');
    var res = {
        filename:    filename,
        extension:    ''
    };
    if(arr.length < 2) return res;
    if(arr[0].length < 1) return res;
    res.extension = arr.pop();
    res.filename = arr.join('.');
    return res;
}

function value(object,key,default_value)
{
    return object ? (object.hasOwnProperty(key) ? object[key] : default_value) : default_value;
}
function makePath(patharr, qsarr, base64encode)
{
    var url = '/' + patharr.join('/')
    var query = makeQueryStr(qsarr);
    url += (query ? '?'+query : '');
    return base64encode ? Base64.encode(url) : url;
}
function makeQueryStr(qsarr)
{
    qs = '';
    for(var key in qsarr){
        qs += key + '=' + encodeURIComponent(qsarr[key]) + '&';
    }
    qs = qs.slice(0,-1);
    return qs;
}
function parseQueryStr(str)
{
    if(str.length < 2)
        return {};
    var data = {};
    var arr = str.split('?');
    var qs = arr.length > 1 ? arr[1] : arr[0];
    var params = qs.split('&');
    for(var a=0;a<params.length;a++) {
        var pa = params[a].split('=');
        data[pa[0]] = pa[1];
    }
    return data;
}
function parsePath(p_str)
{
    return {params: parseQueryStr(p_str), path: splitpath(p_str)};
}
function splitpath(p_path)
{
    var arr = p_path.split('?');
    var path_arr = arr[0].split('/');
    path_arr.clean('');
    return path_arr;
}
function clone(o) {
    return eval('(' + JSON.stringify(o) + ')');
}
function randomString(len, prefix) {
    var chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXTZabcdefghiklmnopqrstuvwxyz";
    var string_length = len;
    if(typeof prefix != 'undefined')
        string_length -= prefix.length
    var randomstring = '';
    for (var i=0; i<string_length; i++) {
        var rnum = Math.floor(Math.random() * chars.length);
        randomstring += chars.substring(rnum,rnum+1);
    }
    return typeof prefix == 'undefined' ? randomstring : prefix + randomstring;
}
String.prototype.ucfirst = function()
{ return this.charAt(0).toUpperCase() + this.substr(1); }

String.prototype.removeLast = function(p_last)
{
    var len = typeof p_last == 'undefined' ? 1 : p_last;
    return this.substring(0, this.length - len);
}
if (typeof String.prototype.splice != 'function') {
    String.prototype.splice = function( idx, s ) {
        return (this.slice(0,idx) + s + this.slice(idx));
    };
}
if (typeof String.prototype.startsWith != 'function') {
  String.prototype.startsWith = function (str){
    return this.slice(0, str.length) == str;
  };
}

String.prototype.getLastWord = function()
{
    if(!this.length)
        return '';
    var words = this.split(' ');
    return words[words.length-1];
}
Array.prototype.clean = function(deleteValue) {
  for (var i = 0; i < this.length; i++) {
    if (this[i] == deleteValue) {
      this.splice(i, 1);
      i--;
    }
  }
  return this;
};
if (!Array.prototype.insert) { //az ECMA monnyon le
    Array.prototype.insert = function(idx, item) {
        this.splice(idx, 0, item);
        return this
    }
}
Array.prototype.quilt = function(item) {
    for(var i = 0; i < this.length-1; i+=2) {
        this.insert(i+1, item);
    }
    return this;
};
String.repeat = function(chr,count)
{
    var str = "";
    for(var x=0;x<count;x++) {str += chr};
    return str;
}
String.prototype.padL = function(width,pad)
{
    if (!width ||width<1)
        return this;

    if (!pad) pad=" ";
    var length = width - this.length
    if (length < 1) return this.substr(0,width);

    return (String.repeat(pad,length) + this).substr(0,width);
}
String.prototype.padR = function(width,pad)
{
    if (!width || width<1)
        return this;

    if (!pad) pad=" ";
    var length = width - this.length
    if (length < 1) this.substr(0,width);
    return (this + String.repeat(pad,length)).substr(0,width);
}
Date.prototype.format = function(p_format)
{
    var date = this;
    if (!p_format)
      p_format="MM/dd/yyyy";

    var month = date.getMonth() + 1;
    var year = date.getFullYear();

    p_format = p_format.replace("MM",month.toString().padL(2,"0"));

    if (p_format.indexOf("yyyy") > -1)
        p_format = p_format.replace("yyyy",year.toString());
    else if (p_format.indexOf("yy") > -1)
        p_format = p_format.replace("yy",year.toString().substr(2,2));

    p_format = p_format.replace("dd",date.getDate().toString().padL(2,"0"));

    var hours = date.getHours();
    if (p_format.indexOf("t") > -1)
    {
       if (hours > 11)
        p_format = p_format.replace("t","pm")
       else
        p_format = p_format.replace("t","am")
    }
    if (p_format.indexOf("HH") > -1)
        p_format = p_format.replace("HH",hours.toString().padL(2,"0"));
    if (p_format.indexOf("hh") > -1) {
        if (hours > 12) hours - 12;
        if (hours == 0) hours = 12;
        p_format = p_format.replace("hh",hours.toString().padL(2,"0"));
    }
    if (p_format.indexOf("mm") > -1)
       p_format = p_format.replace("mm",date.getMinutes().toString().padL(2,"0"));
    if (p_format.indexOf("ss") > -1)
       p_format = p_format.replace("ss",date.getSeconds().toString().padL(2,"0"));

    return p_format;
}
var Map = {
    def: function(p_obj, p_key, p_default)
    {
        return p_obj.hasOwnProperty(p_key) ? p_obj[p_key] : p_default;
    },
    shrink: function(p_object, p_fields)
    {
        foreach(p_object, function(value, key) {
            if(p_fields.indexOf(key) == -1) {
                delete p_object[key];
            }
        });
    },
    shrink_array: function(p_objects, p_fields)
    {
        foreach(p_objects, function(obj, idx) {
            Map.shrink(p_objects[idx], p_fields);
        });
    },
    mine: function(p_obj, p_field)
    {
        var res = [];
        foreach(p_obj, function(item) {
            if(item.hasOwnProperty(p_field))
                res.push(item[p_field]);
        });
        return res;
    },
    insertBefore: function(p_obj, p_key, p_new)
    {
        var tmp = {};
        var found = false;
        for(var key in p_obj) {
            if(key == p_key)
                found = true;
            if(found) {
                tmp[key] = p_obj[key];
                delete p_obj[key];
            }
        }
        for(var key in p_new) {
            p_obj[key] = p_new[key];
        }

        for(var key in tmp) {
            p_obj[key] = tmp[key];
        }
        return p_obj;
    },
    sort: function(p_obj, p_function, p_limit)
    {
        var keys = Map.keys(p_obj);
        keys.sort(p_function);
        var res = [];
        var limit = def(p_limit, 0);
        for(var i=0;i<keys.length;i++) {
            if(limit && i>=limit-1)
                break;
            res.push(p_obj[keys[i]]);
        }
        return res;
    },
    keys: function(p_obj)
    {
        var keys = [];
        for(var k in p_obj) {
            if(p_obj.hasOwnProperty(k))
                keys.push(k);
        }
        return keys;
    },
    key_idx: function(p_obj, p_key)
    {
        var idx = 0;
        for(var key in p_obj) {
            if(key == p_key)
                return idx;
            idx++;
        }
        return -1;
    },
    first_key: function(p_obj)
    {
        for (i in p_obj) return i;
    },
    first: function(p_obj)
    {
        for (i in p_obj) return p_obj[i];
    },
    size: function(p_obj)
    {
        if(typeof p_obj == 'object' && typeof p_obj.length == 'number')
            return p_obj.length;

        var cnt = 0;
        for (name in p_obj) {
            cnt++;
        }
        return cnt;
    },
    init_arr: function(p_obj, p_args, p_value)
    {
        if(p_args.length < 1)
            return;

        var obj = p_obj;

        for(var i = 0; i<p_args.length; i++)
        {
            var key = p_args[i];
            if(!obj.hasOwnProperty(key))
                obj[key] = (i == p_args.length-1 && typeof p_value != 'undefined') ? p_value : {};
            obj = obj[key];
        }
    },
    init: function(p_obj, p_struct)
    {
        if(typeof p_obj != 'object')
            return; //maybe throw sg exception...

        if(!Map.size(p_struct))
            return;

        var obj = p_obj;
        for(var key in p_struct) {
            if(!obj.hasOwnProperty(key))
                obj[key] = p_struct[key];
            Map.init(obj);
        }
    },
    empty: function(p_obj)
    {
        if(typeof p_obj == 'undefined')
            return true;

        var name;
        for (name in p_obj) {
            return false;
        }
        return true;
    },
    merge: function(p_target, p_source)
    {
        for(var key in p_source) {
            if(typeof p_source[key] == 'object')
                Map.merge(p_target[key], p_source[key]);
            else
                p_target[key] = p_source[key];
        }
    },
    merge_options: function(obj1,obj2)
    {
        var obj3 = {};
        for (var attrname in obj1) { obj3[attrname] = obj1[attrname]; }
        for (var attrname in obj2) { obj3[attrname] = obj2[attrname]; }
        return obj3;
    },
    toOptions: function(p_arr, p_titleField, p_addNull)
    {
        var addNull = (p_addNull || false);
        p_titleField = (p_titleField || 'title');

        var res = [];
        if(addNull)
            res[''] = 'none';
        for(var key in p_arr)  {
            res[key] = p_arr[key][p_titleField];
        }
        return res;
    }
}
function foreach(p_obj, p_callback)
{
    for(var i in p_obj) {
        if(p_obj.hasOwnProperty(i)) {
            if(p_callback(p_obj[i], i) == true)
                return false
        }
    }
    return true;
}
function format_timedelta(data)
{
    var desc = {
        sec: 60,
        min: 60,
        hour: 24,
        day: 30,
        month: 12,
        year: 1000
    }

    for(key in desc) {
        var div = desc[key];

        if(data < 2)
            return [data, ' ', span({lm_key: key})];
        else if(data < div) {
            return [data, ' ', span({lm_key: key+'s'})]; //todo: remove this 's' shit
        }

        data = parseInt(data / div);
    }
}
function isElement(obj)
{
  try {
    //Using W3 DOM2 (works for FF, Opera and Chrom)
    return obj instanceof HTMLElement;
  }
  catch(e){
    //Browsers not supporting W3 DOM2 don't have HTMLElement and
    //an exception is thrown and we end up here. Testing some
    //properties that all elements have. (works on IE7)
    return (typeof obj==="object") &&
      (obj.nodeType===1) && (typeof obj.style === "object") &&
      (typeof obj.ownerDocument ==="object");
  }
}