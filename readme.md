**BACKGROUND**

This project is intended to demonstrate site functionality of a multi-user  
blog, complete with member registration/sign-in forms and associated check  
protocols as well as blog post/comment/votes permissioning applied on a  
per-user basis.

The application was developed in Python and is driven by a Google Datastore  
back-end (a NoSQL database) and information is queried through a combination  
of SQL and GQL (Google SQL) queries.

The [blog's](https://multi-user-blog-155503.appspot.com/blog) aesthetics are purposefully chosen to be bare-bones, mirroring  
it's name, 'The Cogwheel Blog' and by default contains postings by three  
registered users (all of which happen to be excerpts from Samuel Taylor Coleridge's  
*The Rime of the Ancient Mariner*).

This site was deployed using the Google App Engine.

**PART I: ACCESSING THE BLOG**  

PUBLIC URL  

The blog site is available through the following public URL:  

https://multi-user-blog-155503.appspot.com/blog  

The main page here has a  help button which will direct you to  
PART II of this document (site usage).  


INSTALLATION & DEPLOYMENT  

As an alternative to access by url, the blog site may also be deployed using  
the Google App Engine.  The blog site was developed in Python with the  
Google App Engine SDK for Python specifically in mind.  

Follow these steps to deploy the site: 

1). Download, install, and initialize the Google Cloud SDK.  
    Installation files and installer packages for various platforms  
    are available here:  
    
    https://cloud.google.com/sdk/docs/  

2). Create a Google Cloud Platform project (you will need a Google account  
    for this - if you don't have one, sign up for one first).  
    Follow the instructions for initializing a Cloud Platform project from  
    the Google cloud account console is available here:  

    https://cloud.google.com/appengine/docs/python/console/  

3). Download the zipped blog files and save them to a local directory.  
    Click on the zipped directory and extract all files.  
    The uncompressed directory should have 'blog/' as the parent directory  
    directly underwhich the app.yaml configuration file and blog.py  
    application should reside.  

4). With the Google Cloud SDK downloaded and installed and a Google Cloud  
    Platform project created, open a terminal session on your computer (if  
    running Windows, enter 'CMD' at the start menu prompt to get the DOS  
    shell).  
    Change directory to the location of the unzipped blog directory and   
    run the following command form directly under the blog directory (at  
    the same level as where the app.yaml file resides):  

    gcloud app deploy app.yaml index.yaml --project <projectname>  

    where <projectname> is the name of the Google Cloud project created  
    for this purpose.  

    Follow the instructions in the terminal.  

    When the deployment/upload is completed, a URL will be given where  
    the application has been deployed and can be accessed.  

5). For more information on deploying an app using the Google App Engine, see  
    the following links:  

    https://cloud.google.com/appengine/docs/python/tools/uploadinganapp  
    https://cloud.google.com/appengine/docs/python/getting-started/deploying-the-application  



**PART II: SITE USAGE INSTRUCTIONS**


**WELCOME**

Welcome to The Cogwheel Blog!

Blog articles on the site may be read by anyone regardless of registration
and/or logged-in status.

To make full use of the functionality of the site, you must be a registered user  
and logged-in to a given session.  Registering and logging allow user functions  
such as posting/editing/deleting blog posts and comments as well as voting blog  
posts up or down.  

When not logged in, you may browse and read posts on the main page and/or click  
on individual posts to render and read that specific article.  

Comments are viewable only by logged-in users and voting functionality  
is similarly restricted to logged-in users only.  
  
  
**REGISTRATION**

In order to register on the site, simply click the 'register' button.  You will  
be directed to a register form in which you must enter your username and  
password.  An email address is optional.  

Usernames and passwords must be at least 3 characters long and passwords are  
verified during registration with a second password entry to ensure it matches  
the first one. If provided, a valid email address is also checked for validity.  

Errors on this page will be raised to alert the user to one or more of the  
following conditions:  
    1). Invalid logon  
    2). Passwords not matching  
    3). Invalid email address  
    4). User already exists  


**LOGGING IN**  

If you have already registered, you may simply click the 'login' button in the  
top menu to log into a session.  

Enter your username and password in the log in menu.  

Possible errors you might encounter here include:  
    1). No such user exists (in which case, register first!)  
    2). Invalid login (check your username and password)  

Both the register and log-in menus provide for a convenient way to perform the  
alternate action, depending on circumstances.  


**POSTING**  

You must be registered and log in to post an article.  

Once logged-in, the main menu options will be changed to offer:  
    1). newpost - click this to make a new post.  Note that valid articles  
        require both a subject and content and posts violating this condition  
        will not be submitted.  Once finished, click submit.  
    2). logout - click this to log out of a session.  


**EDITING/DELETING POSTS**  

You may only edit or delete your own posts.  

Once logged in, click on a post/article title to be directed to that particular  
article.  The menu options will change to offer:  
    1). editpost - click this to edit your post.  Note that the requirements of  
        a valid subject and content will still apply.  Click submit at the  
        bottom when finished editing.  
    2). delete - click this to delete a post.  

Note that editing and deletion options are separated and an error will be raised  
to reflect this if you attempt to edit a post to deletion by submitting empty  
subject and content entries.  

Note that post author and session user credentials are cross-checked for editing  
and/or deletion functionality.  An error is raised if you attempt to edit or  
delete a post that is not your own.  


**COMMENTING**  

Commenting functionality is available to logged-in users only.  

Comments appear at the end (bottom) of posted articles. You may comment on  
anyone's blog post, including your own.  Comments are grouped together by blog  
post and are presented in descending time-stamped order.  

In order to make or add a comment, simply click the 'comment' button at the end  
of a particular posting to comment on that particular article.  

Unlike posts, comments do not require a subject.  

**EDITING/DELETING COMMENTS**  

You may only edit or delete your own comments and an error is raised if your  
log-in credentials do not match those of the comment author.  

Similar to posts, editing and deletion functionality are separated so you may  
not edit a comment to deletion by attempting to provide empty content.  Use the  
'delete' button to do this, instead.  

Comment functionality includes:  
    1). edit - click this to edit a comment  
    2). delete - click this to delete a comment.  


**VOTING**  

Votes per blog posting/article are viewable to anyone and appear both in the  
main page listing all articles as well as in individual article pages.  

For each blog post, a green up-arrow in the top left-hand corner above the blog  
title will indicate the aggregate number of up votes the post has received  
whereas the red down-arrow indicates the aggregate number of down-votes.  

Voting is restricted to logged-in users.  

In order to vote up or down a post, log-in and simply click either the up arrow  
or the down arrow above the post title to indicate your preference.  

You may not vote for your own post and you may only vote in the same direction  
for a given post once.  Changing votes is allowed - thus, if you once down-voted  
a post and decided to up-vote it, you may do so.  Multiple attempts to vote in  
the same direction, however, are not allowed.  

The following self-explanatory messages may appear when using voting  
functionality:  
    1). Upvote has been recorded  
    2). Downvote has been recorded  
    3). Your like vote has been already registered  
    4). Your dislike vote has been alredy registered  
    5). Cannot vote for your own posts!  

**ENJOY THE BLOG!!**