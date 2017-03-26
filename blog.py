import os
import re
import string
import random
import hashlib

import webapp2
import jinja2

from google.appengine.ext import db

# ---global settings-------------------------------------------------

# ---template utilities
temp_sub_dir = "www/content/html"
template_dir = os.path.join(os.path.dirname(__file__), temp_sub_dir)
jinja_env = jinja2.Environment(
                                loader=jinja2.FileSystemLoader(template_dir),
                                autoescape=True)

# ---task-specific
NUM_ARTICLES = 10       # ---blog entries to display on main page
RAND_LEN1 = 5
RAND_LEN2 = 12
# ---randomly generated secret salt this session:
SESSION_WORD = ''.join(random.choice(string.letters)
                       for x in xrange(RAND_LEN1))

# -------------------------------------------------------------------


# ===global utilities:=========================================================

# ---set template----------------------------------------------------

def render_str(template, **params):
    outPage = jinja_env.get_template(template)
    return outPage.render(params)


def blog_key(name='default'):
    return db.Key.from_path('blogs', name)


def comment_key(name='default'):
    return db.Key.from_path('comments', name)

# ---page display----------------------------------------------------

class RenderPage(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        return render_str(template, **params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

# ---check security--------------------------------------------------

def gen_hashval(val, *salt):
    if not salt:
        salt = SESSION_WORD
    return '%s|%s' % (val, hashlib.sha256(str(salt) + val).hexdigest())


def crosscheck_user(regUser, userid_cookie):
    if userid_cookie == gen_hashval(regUser.split('|')[0],
                                    regUser.split('|')[1]):
        return userid_cookie


# ---registration utilities------------------------------------------

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
    return username and USER_RE.match(username)

PASS_RE = re.compile(r"^.{3,20}$")
def valid_password(password):
    return password and PASS_RE.match(password)

EMAIL_RE  = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
def valid_email(email):
    return not email or EMAIL_RE.match(email)

def make_salt():
    return ''.join(random.choice(string.letters) for x in xrange(RAND_LEN2))

def make_pw_hash(name, pw, salt=None):
    if not salt:
        salt = make_salt()
    hashPassword = hashlib.sha256(name + pw + str(salt)).hexdigest()
    return '%s, %s' % (hashPassword, salt)

# -------------------------------------------------------------------

# =============================================================================


# ===data models:==============================================================

class Post(db.Model):
    author = db.StringProperty(required=True)
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    likes = db.IntegerProperty()
    dislikes = db.IntegerProperty()
    created = db.DateTimeProperty(auto_now_add=True)
    last_modified = db.DateTimeProperty(auto_now=True)

    def render(self):
        self._render_text = self.content.replace('\n', '<br>')
        return render_str("post.html", p=self)


class Users(db.Model):
    username = db.StringProperty(required=True)
    password = db.StringProperty(required=True)
    email = db.StringProperty(required=False)
    # ---note: using per user salt from registration
    salt = db.StringProperty(required=True)
    create_time = db.DateTimeProperty(auto_now_add=True)


class Comments(db.Model):
    post_id = db.IntegerProperty(required=True)
    username = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    create_time = db.DateTimeProperty(auto_now_add=True)
    last_modified = db.DateTimeProperty(auto_now=True)


class Votes(db.Model):
    post_id = db.IntegerProperty(required=True)
    user_id = db.IntegerProperty(required=True)
    like = db.IntegerProperty()
    dislike = db.IntegerProperty()
    updated = db.DateTimeProperty(auto_now=True)

# =============================================================================


# ====registration:============================================================

class Register(RenderPage):

    def get(self):
        self.render("register.html")

    def post(self):
        have_error = False
        username = self.request.get('username')
        password = self.request.get('password')
        verify = self.request.get('verify')
        email = self.request.get('email')

        params = dict()

        if not valid_username(username):
            params['error_username'] = "Invalid username."
            have_error = True

        if not valid_password(password):
            params['error_password'] = "Invalid password."
            have_error = True
        elif password != verify:
            params['error_verify'] = "Passwords don't match."
            have_error = True

        if not valid_email(email):
            params['error_email'] = "Invalid email."
            have_error = True

        query = "SELECT * FROM Users WHERE username = \'" + username + "\'"
        userQuery = db.GqlQuery(query)

        for uname in userQuery:
            if uname.username == username:
                params['error_userexists'] = "User already exists."
                have_error = True

        if have_error:
            self.render('register.html', **params)
        else:
            hashpassword = make_pw_hash(username, password)
            record = Users(username=username,
                           password=hashpassword.split(', ')[0],
                           email=email,
                           salt=hashpassword.split(', ')[1])
            record.put()

            # ---would prefer avoiding use of global variables
            global regUsername
            regUsername = username
            global regUser
            regUser = str(record.key().id())+"|"+record.salt

            # ---set a secure cookie as: user_id | hash(user_id + SESSION_WORD)
            secure_cookie = gen_hashval(str(record.key().id()), record.salt)
            self.response.headers['Content-Type'] = 'text/plain'
            self.response.headers.add_header('Set-Cookie',
                                             '%s = %s; Path = /'
                                             % ('user_id', secure_cookie))

            self.redirect('/blog/welcome')

# =============================================================================


# ===login:====================================================================

'''
need to change hash technique from sha256 to bcrypt.

'''

class Login(RenderPage):

    def get(self):
        self.render("login.html")

    def post(self):
        have_error = False
        username = self.request.get('username')
        password = self.request.get('password')

        params = dict()

        query = "SELECT * FROM Users WHERE username=\'" + username + "\'"
        userQuery = db.GqlQuery(query).get()

        if userQuery:
            baseUser = userQuery.username
            basePass = userQuery.password
            salt = userQuery.salt
            candHash = make_pw_hash(username, password, salt)

            if candHash.split(', ')[0] == basePass:
                secure_cookie = gen_hashval(str(userQuery.key().id()), salt)
                self.response.set_cookie('user_id', secure_cookie)

                global regUsername
                regUsername = username
                global regUser
                regUser = str(userQuery.key().id())+"|"+salt

                self.redirect('/blog/welcome')
            else:
                have_error = True
        else:
            have_error = True

        if have_error:
            params['error_invalidLogin'] = "Invalid Login"
            if not userQuery:
                params['error_invalidLogin'] = "No such user exists."
            self.render("login.html", **params)

# =============================================================================


# ===welcome:==================================================================

class Welcome(RenderPage):
    def get(self):
        userid_cookie = self.request.cookies.get('user_id')
        if userid_cookie:
            if crosscheck_user(regUser, userid_cookie):
                self.render('welcome.html', username=regUsername)
            else:
                self.redirect('/blog/register')
        else:
            self.redirect('/blog/register')

# =============================================================================


# ===blog main page:===========================================================

class BlogMain(RenderPage):
    def get(self):
        query = "select * from Post order by created desc limit "
        query += str(NUM_ARTICLES)
        posts = db.GqlQuery(query)

        try:
            self.render('front.html', posts=posts, username=regUsername)
        except NameError:
            self.render('front_null.html', posts=posts, username="", error="")

# =============================================================================


# ===new post:=================================================================

class NewPost(RenderPage):

    def get(self):
        userid_cookie = self.request.cookies.get('user_id')
        if not userid_cookie:
            self.redirect('/blog/login')
        else:
            if crosscheck_user(regUser, userid_cookie):
                self.render('newpost.html', username=regUsername)
            else:
                self.redirect('/blog/register')

    def post(self):
        subject = self.request.get('subject')
        content = self.request.get('content')

        userid_cookie = self.request.cookies.get('user_id')
        if not userid_cookie:
            self.redirect('/blog/login')

        user_id = self.request.cookies.get('user_id').split('|')[0]
        key = db.Key.from_path('Users', int(user_id), parent=None)
        author = db.get(key)
        author = author.username

        if not author:
            self.render("front_null.html", subject=subject, content=content,
                        login_error="Must be logged in to post!")
        else:
            if subject and content:
                p = Post(parent=blog_key(), author=author, subject=subject,
                         content=content, likes=0, dislikes=0)
                p.put()
                self.redirect('/blog/%s' % str(p.key().id()))
            else:
                error = "Posts require a subject and some content."
                try:
                    self.render("newpost.html", subject=subject,
                                content=content, error=error,
                                username=regUsername)
                except NameError:
                    self.render("newpost.html", subject=subject,
                                content=content, error=error)

# =============================================================================


# ===post page:================================================================

class PostPage(RenderPage):
    def get(self, post_id):
        # ---fetch post content
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)

        # ---fetch associated comments
        comments = Comments.all()
        comments.filter("post_id = ", int(post_id))
        comments.order('-create_time')

        if not post:
            self.error(404)
            return
        try:
            if comments:
                self.render("permalink.html", post=post, username=regUsername,
                            comments=comments)
            else:
                self.render("permalink.html", post=post, username=regUsername)
        except NameError:
            self.render("permalink_null.html", post=post, username="")

# =============================================================================


# ===edit post:================================================================

class EditPost(RenderPage):
    def get(self, post_id):
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)

        # ---check if user credentials match post's author
        query = "SELECT * FROM Users WHERE username=\'" + post.author + "\'"
        authorQuery = db.GqlQuery(query).get()
        author_cred = gen_hashval(str(authorQuery.key().id()),
                                  authorQuery.salt)

        if author_cred == self.request.cookies.get('user_id'):
            self.render("editpost.html", subject=post.subject,
                        content=post.content, username=regUsername)
        else:
            self.render("permalink.html", post=post, username=regUsername,
                        error="Must be author of post to edit!")

    def post(self, post_id):
        # ---get modified content from edited post:
        subject = self.request.get('subject')
        content = self.request.get('content')

        if not (subject and content):
            error = "Posts require a subject and some content. "
            error += "Use 'delete' to remove posts."
            self.render("editpost.html", subject=subject, content=content,
                        username=regUsername, error=error)
        else:
            key = db.Key.from_path('Post', int(post_id), parent=blog_key())
            post = db.get(key)
            post.subject = subject
            post.content = content
            post.put()
            self.redirect('/blog/%s' % str(post_id))

# =============================================================================


# ===delete post:==============================================================

class DeletePost(RenderPage):
    def get(self, post_id):
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)

        # ---check if user credentials match post's author
        query = "SELECT * FROM Users WHERE username=\'" + post.author + "\'"
        authorQuery = db.GqlQuery(query).get()
        author_cred = gen_hashval(str(authorQuery.key().id()),
                                  authorQuery.salt)

        if author_cred == self.request.cookies.get('user_id'):
            post.delete()
            self.render("confirmation.html", post=post, username=regUsername,
                        message="This post has been deleted.")
        else:
            self.render("permalink.html", post=post, username=regUsername,
                        error="Must be author of post to delete!")

# =============================================================================


# ===new comment:==============================================================

class NewComment(RenderPage):
    def get(self, post_id):
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)
        self.render("newcomment.html", author=regUsername,
                    subject=post.subject, username=regUsername)

    def post(self, post_id):
        content = self.request.get('content')
        newcomment = Comments(post_id=int(post_id), username=regUsername,
                              content=content)
        newcomment.put()
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)
        self.render("confirmation.html", post=post, username=regUsername,
                    message="Comment has been posted.")

# =============================================================================


# ===edit comment:=============================================================

class EditComment(RenderPage):
    def get(self, comment_id):

        key = db.Key.from_path('Comments', int(comment_id), parent=None)
        comment = db.get(key)

        key = db.Key.from_path('Post', comment.post_id, parent=blog_key())
        post = db.get(key)

        # ---check if user credentials match comment's author
        query = "SELECT * FROM Users WHERE username=\'"
        query += comment.username + "\'"
        authorQuery = db.GqlQuery(query).get()
        user_id = self.request.cookies.get('user_id').split('|')[0]

        if int(authorQuery.key().id()) == int(user_id):
            self.render("editcomment.html", content=comment.content,
                        username=regUsername)
        else:
            self.render("permalink.html", post=post, username=regUsername,
                        error="Must be author of comment to edit!")

    def post(self, comment_id):
        # ---get modified content from edited comment:
        content = self.request.get('content')

        if not content:
            error = "Comments require content. Use 'delete' to remove comment."
            self.render("editcomment.html", content=content,
                        username=regUsername, error=error)
        else:
            key = db.Key.from_path('Comments', int(comment_id), parent=None)
            comment = db.get(key)
            comment.content = content
            comment.put()
            key = db.Key.from_path('Post', comment.post_id, parent=blog_key())
            post = db.get(key)
            self.render("confirmation.html", post=post, username=regUsername,
                        message="Comment has been updated.")

# =============================================================================


# ===delete comment:===========================================================

class DelComment(RenderPage):
    def get(self, comment_id):
        key = db.Key.from_path('Comments', int(comment_id), parent=None)
        comment = db.get(key)

        key = db.Key.from_path('Post', comment.post_id, parent=blog_key())
        post = db.get(key)

        # ---check if user credentials match post's author
        query = "SELECT * FROM Users WHERE username=\'"
        query += comment.username + "\'"
        authorQuery = db.GqlQuery(query).get()
        author_cred = gen_hashval(str(authorQuery.key().id()),
                                  authorQuery.salt)

        if author_cred == self.request.cookies.get('user_id'):
            comment.delete()
            self.render("confirmation.html", post=post, username=regUsername,
                        message="Comment has been deleted.")
        else:
            self.render("permalink.html", post=post, username=regUsername,
                        error="Must be author of comment to delete!")

# =============================================================================


# ===vote:=====================================================================

'''
1). Check1: logged status (votes disallowed if not logged in)
2). Check2: disallow vote if user = post author
3). Check3: check if user has already voted for this posting
    a). If no record of a vote, register vote received.
    b). Avoid double counts if user is attempting to register another
        vote in same direction
    c). Allow user to change vote if previous vote was in opposite direction
'''

# ---upvotes (likes)-------------------------------------------------

class Like(RenderPage):
    def get(self, post_id):
        # ---fetch post content
        postkey = db.Key.from_path('Post', int(post_id), parent=blog_key())
        postbody = db.get(postkey)

        # ---fetch associated comments
        comments = Comments.all()
        comments.filter("post_id = ", int(post_id))
        comments.order('-create_time')

        # ---check1:
        regUser = self.request.cookies.get('user_id')

        # ---check2: check if user = post author
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)

        query = "SELECT * FROM Users WHERE username=\'" + post.author + "\'"
        authorQuery = db.GqlQuery(query).get()
        user_id = self.request.cookies.get('user_id').split('|')[0]

        if int(authorQuery.key().id()) == int(user_id):
            error = "Cannot vote on your own posts!"
            self.render("permalink.html", post=postbody, username=regUsername,
                        comments=comments, error=error)
        else:
            # ---check 3:
            user_id = self.request.cookies.get('user_id').split('|')[0]
            query = "SELECT * FROM Votes WHERE post_id = " + post_id
            query += " AND user_id = " + user_id
            voteQuery = db.GqlQuery(query).get()
            if (voteQuery and voteQuery.like == 1):
                error = "Your like vote has already been registered."
                self.render("permalink.html", post=postbody,
                            username=regUsername, comments=comments,
                            error=error)
            else:
                if voteQuery:
                    votekey = db.Key.from_path('Votes', voteQuery.key().id(),
                                               parent=None)
                    vote = db.get(votekey)
                    vote.like = 1
                    vote.dislike = 0
                else:
                    vote = Votes(post_id=int(post_id), user_id=int(user_id),
                                 like=1, dislike=0)
                post.likes += 1
                if (voteQuery and voteQuery.dislike == 1):
                    post.dislikes -= 1
                vote.put()
                post.put()
                msg = "Upvote has been recorded."
                self.render("permalink.html", post=postbody,
                            username=regUsername, error=msg)

# -------------------------------------------------------------------


# ---downvotes (dislikes)--------------------------------------------

class Dislike(RenderPage):
    def get(self, post_id):
        # ---fetch post content
        postkey = db.Key.from_path('Post', int(post_id), parent=blog_key())
        postbody = db.get(postkey)

        # ---fetch associated comments
        comments = Comments.all()
        comments.filter("post_id = ", int(post_id))
        comments.order('-create_time')

        # ---check1:
        regUser = self.request.cookies.get('user_id')

        # ---check2: check if user = post author
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)

        query = "SELECT * FROM Users WHERE username=\'" + post.author + "\'"
        authorQuery = db.GqlQuery(query).get()
        user_id = self.request.cookies.get('user_id').split('|')[0]

        if int(authorQuery.key().id()) == int(user_id):
            error = "Cannot vote on your own posts!"
            self.render("permalink.html", post=postbody, username=regUsername,
                        comments=comments, error=error)
        else:
            # ---check 3:
            user_id = self.request.cookies.get('user_id').split('|')[0]
            query = "SELECT * FROM Votes WHERE post_id=" + post_id
            query += " AND user_id = " + user_id
            voteQuery = db.GqlQuery(query).get()
            if (voteQuery and voteQuery.dislike == 1):
                error = "Your dislike vote has already been registered."
                self.render("permalink.html", post=postbody,
                            username=regUsername, comments=comments,
                            error=error)
            else:
                if voteQuery:
                    votekey = db.Key.from_path('Votes', voteQuery.key().id(),
                                               parent=None)
                    vote = db.get(votekey)
                    vote.dislike = 1
                    vote.like = 0
                else:
                    vote = Votes(post_id=int(post_id), user_id=int(user_id),
                                 like=1, dislike=0)
                post.dislikes += 1
                if (voteQuery and voteQuery.like == 1):
                    post.likes -= 1
                vote.put()
                post.put()
                msg = "Downvote has been recorded."
                self.render("permalink.html", post=postbody,
                            username=regUsername, error=msg)

# -------------------------------------------------------------------

# =============================================================================


# ===help:=====================================================================

class Help(RenderPage):
    def get(self):
        self.render("help.html", post="", username="")

# =============================================================================


# ===logout:===================================================================

class Logout(RenderPage):
    def get(self):
        self.response.set_cookie('user_id', "")
        self.redirect('/blog/login')
        global regUsername
        try:
            del regUsername
        except NameError:
            self.redirect('/blog/login')

# =============================================================================


# ===resource handlers=========================================================

app = webapp2.WSGIApplication([    ('/blog/register', Register)
                                 , ('/blog/welcome', Welcome)
                                 , ('/blog/login', Login)
                                 , ('/blog/logout', Logout)
                                 , ('/blog/help', Help)
                                 , ('/blog/?', BlogMain)
                                 , ('/blog/newpost', NewPost)
                                 , ('/blog/([0-9]+)', PostPage)
                                 , ('/blog/([0-9]+)/editpost', EditPost)
                                 , ('/blog/([0-9]+)/deletepost', DeletePost)
                                 , ('/blog/([0-9]+)/newcomment', NewComment)
                                 , ('/blog/([0-9]+)/editcomment', EditComment)
                                 , ('/blog/([0-9]+)/deletecomment', DelComment)
                                 , ('/blog/([0-9]+)/like', Like)
                                 , ('/blog/([0-9]+)/dislike', Dislike)
                              ], 
                              debug=True)

# =============================================================================
