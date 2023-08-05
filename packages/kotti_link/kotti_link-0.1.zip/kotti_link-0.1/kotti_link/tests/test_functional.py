from pytest import mark


@mark.user('admin')
def test_add_link(webtest):

    resp = webtest.get('/add_link')

    # submit empty form
    form = resp.forms['deform']
    form['title'].value = 'Google'
    form['link'].value = 'http://google.com'
    resp = form.submit('save')
    assert resp.status_code == 302
    resp = resp.follow()
    # Ok, saved correctly
    assert 'Item was added.' in resp.body

    # Let's open the edit form of our link
    resp = webtest.get('/google/@@edit')
    form = resp.forms['deform']
    assert form['title'].value == 'Google'
    assert form['link'].value == 'http://google.com'
