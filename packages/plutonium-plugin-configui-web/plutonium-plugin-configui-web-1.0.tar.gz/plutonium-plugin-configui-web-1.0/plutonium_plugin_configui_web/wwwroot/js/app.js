
function Application(cont, default_page, models, lm)
{
	var m_self = this;
	var m_crud = new sqlchemyforms.widgets.crud(cont, '/api', models, lm);

    m_self.update_links = function()
    {
        $('a[href^="/"]').address();
    }

	m_self.change_url = function(event)
	{
		$('.navbar-nav li').removeClass('active');

		if(event.pathNames.length) {
			$('.navbar-nav li[pl-menu='+event.pathNames[0]+']').addClass('active');
		}

		if(event.pathNames.length > 0)
			m_crud.load(event.value);
		else
			cont.set(div({lm_key: 'about'}));
	}
}
