
/**
 * params:
 *  - [cookie_key]: set the code in the cookies with this key
 *  - [on_change_language]: callback when changes the current lang
 *  - [lang_api_url]: if lang data is loadable through webservice (the GET params: code = en|hu etc..)
 */
sqlchemyforms.language_manager = function(params)
{
    var m_self = this;
    var m_data = {}
    var m_curr_lang = '';

    m_self.init = function(code, data)
    {
        m_data[code] = data;
        m_self.set_flag(code);
        m_curr_lang = code;
    }

    m_self.add_lang_data = function(code, data)
    {
        m_data[code] = data;
    }

    m_self.load = function(code)
    {
        if(m_curr_lang == code)
            return

        if(code in m_data) {
            m_self.set_lang(code);
            return
        }

        if('lang_api_url' in params) {
            $.get(params.lang_api_url, {code: code}, function(raw) {
                m_self.add_lang_data(code, JSON.parse(raw).data);
                m_self.set_lang(code);
            });
        }
    }

    m_self.set_flag = function(code)
    {
        if('on_change_language' in params)
            params.on_change_language(code);
    }

    m_self.update = function()
    {
        console.debug('sqlchemyforms.language_manager::update');

        $('[lm_key]').each(function(idx, element) {
            var el = _cl(element)
            var key = el.p('lm_key');
            var value = m_self.get(key);
            var attr = el.p('lm_attr');
            if(attr == null)
                el.html(value);
            else
                el.p(attr, value);
        });
    }

    m_self.set_lang = function(code)
    {
        m_curr_lang = code;

        if('cookie_key' in params)
            $.cookie(params.cookie_key, code);

        m_self.set_flag(code);

        m_self.update();
    }

    m_self.template = function(str, data)
    {
        var re = /<%([^%>]+)?%>/g, match;
        while(match = re.exec(str)) {
            str = str.replace(match[0], data[match[1]])
        }
        return str;
    }

    m_self.get = function(key, data)
    {
        if(!(m_curr_lang in m_data))
            return key;

        var lang = m_data[m_curr_lang];
        if(key in lang)
            return typeof data == 'object' ? m_self.template(lang[key], data) : lang[key];
        return key;
    }
}
