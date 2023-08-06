import tiny, os

app = tiny.TinyApp()

app.set_template_path(os.path.abspath('tiny/templates'))

## Routing ###

@app.route('/')
def index(request):

	content = tiny.TinyResponse(app.render('test_render.html', test_var="testing", cool_var="cool beans", yo_DAWG="yo dawg"))
	return content

@app.route('/505')
def error(request):

	content = tiny.TinyResponse('HTTP Version Not Supported', 505)
	return content

@app.route('/user')
def user(request):
	if request.get_data != {}:
		return tiny.TinyResponse('<h1>Hello %s!</h1>' % (request.get_data['name']))
	else:
		return tiny.TinyResponse('<h1>User not found.</h1>')

@app.route('/post_test')
def post_test(request):
	if request.post_data != None:
		return tiny.TinyResponse('<b>Your favorite movie is %s!?!?!?''' % (request.post_data['movie']))
	else:
		return tiny.TinyResponse('''<h1>My Form</h1><form action="/post_test" method="post"><input type="text" name="movie" placeholder="Favorite Movie"></input></form>''')

if __name__ == '__main__':
	tiny.run_app(app)